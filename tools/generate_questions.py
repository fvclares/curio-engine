#!/usr/bin/env python3
"""Gera novas perguntas de quiz usando a API do Google Gemini.

Uso:
    python tools/generate_questions.py --category "Espaço" --quantity 5
    python tools/generate_questions.py --category "Curiosidades" --quantity 10 --dry-run

Requer a variável de ambiente GEMINI_API_KEY (gratuita em
https://aistudio.google.com/app/apikey).

O script:
  1. Lê data/questions.json (se existir) para colher prompts antigos como referência de contexto.
  2. Pede ao Gemini N novas perguntas na categoria informada, em JSON estruturado.
  3. Valida cada pergunta (4 alternativas, exatamente 1 correta, id único).
  4. SOBRESCREVE o questions.json, excluindo as perguntas antigas e salvando apenas as novas.

As perguntas novas NÃO vêm com áudio — rode depois
`python tools/generate_audio.py` (ou o workflow "Gerar áudio") para narrá-las.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUESTIONS_PATH = PROJECT_ROOT / "data" / "questions.json"

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

RESPONSE_SCHEMA = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "prompt": {"type": "STRING"},
            "explanation": {"type": "STRING"},
            "answers": {
                "type": "ARRAY",
                "minItems": 4,
                "maxItems": 4,
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "text": {"type": "STRING"},
                        "isCorrect": {"type": "BOOLEAN"},
                    },
                    "required": ["text", "isCorrect"],
                },
            },
        },
        "required": ["prompt", "explanation", "answers"],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera novas perguntas de quiz via Gemini.")
    parser.add_argument("--category", required=True, help="Categoria das novas perguntas (ex: 'Espaço').")
    parser.add_argument("--quantity", type=int, default=5, help="Quantas perguntas gerar (padrão: 5).")
    parser.add_argument(
        "--questions",
        default=str(DEFAULT_QUESTIONS_PATH),
        help=f"Caminho do questions.json (padrão: {DEFAULT_QUESTIONS_PATH})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra as perguntas geradas sem salvar no arquivo.",
    )
    return parser.parse_args()


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return slug[:40]


def load_questions(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else data.get("questions", [])
    except (json.JSONDecodeError, OSError):
        return []


def save_questions(path: Path, questions: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")


def build_prompt(category: str, quantity: int, existing_prompts: List[str]) -> str:
    avoid = "\n".join(f"- {p}" for p in existing_prompts[-40:]) or "(nenhuma ainda)"
    return f"""Você é um redator de quiz educativo em português do Brasil.

Gere {quantity} perguntas de múltipla escolha NOVAS e ORIGINAIS sobre o tema: "{category}".

Regras obrigatórias:
- Cada pergunta tem exatamente 4 alternativas, sendo exatamente 1 correta.
- As alternativas erradas devem ser plausíveis, não óbvias.
- A explicação deve ter 1 a 3 frases, factual e didática.
- Não repita nem parafraseie estas perguntas já existentes:
{avoid}
- Nada de opinião, política controversa ou conteúdo sensível.
- Responda em português do Brasil.
"""


def call_gemini(api_key: str, category: str, quantity: int, existing_prompts: List[str]) -> List[Dict[str, Any]]:
    payload = {
        "contents": [{"parts": [{"text": build_prompt(category, quantity, existing_prompts)}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
            "temperature": 1.0,
        },
    }
    request = urllib.request.Request(
        f"{GEMINI_URL}?key={api_key}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"Erro da API Gemini ({exc.code}): {detail}") from exc

    try:
        text = body["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Resposta inesperada do Gemini: {body}") from exc


def validate_question(raw: Dict[str, Any]) -> bool:
    answers = raw.get("answers", [])
    if len(answers) != 4:
        return False
    correct = [a for a in answers if a.get("isCorrect")]
    if len(correct) != 1:
        return False
    if not raw.get("prompt") or not raw.get("explanation"):
        return False
    return True


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Erro: defina a variável de ambiente GEMINI_API_KEY.", file=sys.stderr)
        return 1

    questions_path = Path(args.questions).resolve()
    old_questions = load_questions(questions_path)
    existing_prompts = [q["prompt"] for q in old_questions if "prompt" in q]

    print(f"Pedindo {args.quantity} perguntas novas sobre '{args.category}' ao Gemini ({GEMINI_MODEL})...")
    
    try:
        raw_questions = call_gemini(api_key, args.category, args.quantity, existing_prompts)
    except RuntimeError as exc:
        print(f"Erro fatal: {exc}", file=sys.stderr)
        return 1

    accepted: List[Dict[str, Any]] = []
    generated_ids: set[str] = set()

    for raw in raw_questions:
        if not validate_question(raw):
            print(f"  ⚠️  Pergunta descartada (formato inválido): {raw.get('prompt', '???')[:60]}")
            continue

        base_id = f"{slugify(args.category)}-{slugify(raw['prompt'])}"
        question_id = base_id
        suffix = 2
        while question_id in generated_ids:
            question_id = f"{base_id}-{suffix}"
            suffix += 1
        generated_ids.add(question_id)

        accepted.append(
            {
                "id": question_id,
                "category": args.category,
                "prompt": raw["prompt"],
                "answers": raw["answers"],
                "explanation": raw["explanation"],
            }
        )
        print(f"  ✅ {question_id}: {raw['prompt'][:70]}")

    if not accepted:
        print("Nenhuma pergunta válida foi gerada.")
        return 1

    if args.dry_run:
        print(f"\n[--dry-run] {len(accepted)} perguntas seriam geradas. Nada foi salvo.")
        return 0

    # Sobrescreve o arquivo gravando APENAS o novo lote gerado
    save_questions(questions_path, accepted)
    
    print(f"\n{len(accepted)} pergunta(s) salva(s) em {questions_path} (perguntas anteriores excluídas).")
    print("Rode 'python tools/generate_audio.py' para gerar as novas narrações e limpar áudios antigos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
