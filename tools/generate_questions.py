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

# Limites de tamanho pensados para o card do quiz (tela cheia, fonte grande,
# sem scroll). Se ficar maior que isso, o texto estoura o card — é por isso
# que o prompt e a validação abaixo também cobram frases curtas e diretas.
MAX_PROMPT_CHARS = 110
MAX_ANSWER_CHARS = 28
MAX_EXPLANATION_CHARS = 170

RESPONSE_SCHEMA = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "prompt": {"type": "STRING", "maxLength": str(MAX_PROMPT_CHARS)},
            "explanation": {"type": "STRING", "maxLength": str(MAX_EXPLANATION_CHARS)},
            "answers": {
                "type": "ARRAY",
                "minItems": 4,
                "maxItems": 4,
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "text": {"type": "STRING", "maxLength": str(MAX_ANSWER_CHARS)},
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
    return f"""Você é um redator de quiz de CURIOSIDADES para redes sociais (estilo Reels/TikTok),
em português do Brasil. O tom é leve, divertido e fácil de ler em 3 segundos — pense em
"você sabia que..." e não em prova escolar ou aula de história da arte.

Gere {quantity} perguntas de múltipla escolha NOVAS e ORIGINAIS sobre o tema: "{category}".

O que TORNA uma boa pergunta aqui:
- Um fato curioso, surpreendente, engraçado ou "uau" sobre o tema — recorde, número
  estranho, origem inusitada, coincidência, comparação inesperada.
- Linguagem simples, de conversa. Zero jargão técnico, zero termo acadêmico sem explicar.
- Pergunta CURTA: uma frase só, direto ao ponto (até {MAX_PROMPT_CHARS} caracteres).

O que EVITAR (motivo pelo qual perguntas antigas foram descartadas):
- Perguntas técnicas ou de "livro didático": nomes de técnicas, estilos, correntes,
  processos físicos/químicos detalhados, datas exatas decoradas, jargão de especialista.
- Frases longas, com várias orações encaixadas ou explicações embutidas na própria pergunta.
- Perguntas que soam como prova de vestibular em vez de curiosidade de feed.

Formato de cada pergunta:
- "prompt": a pergunta em si. UMA frase curta e direta, no máximo {MAX_PROMPT_CHARS}
  caracteres. Ex: "Qual animal consegue dormir com um olho aberto?" em vez de
  "Qual mecanismo neurológico permite que certas espécies mantenham vigília hemisférica?".
- "answers": exatamente 4 alternativas, 1 correta. Cada alternativa é uma palavra ou
  frase bem curta (no máximo {MAX_ANSWER_CHARS} caracteres) — nada de frases completas
  como resposta. As erradas devem ser plausíveis e do mesmo "tamanho" da certa, sem ser óbvias.
- "explanation": 1 a 2 frases CURTAS (no máximo {MAX_EXPLANATION_CHARS} caracteres no total),
  contando o fato curioso de um jeito animado, tipo comentando com um amigo — não uma
  explicação técnica de como/por que algo funciona.

Não repita nem parafraseie estas perguntas já existentes:
{avoid}

Nada de opinião, política controversa ou conteúdo sensível.
Responda em português do Brasil.
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

    # Segunda barreira contra texto grande demais para o card, caso o
    # modelo ignore o maxLength do schema.
    if len(raw["prompt"]) > MAX_PROMPT_CHARS:
        return False
    if len(raw["explanation"]) > MAX_EXPLANATION_CHARS:
        return False
    if any(len(a.get("text", "")) > MAX_ANSWER_CHARS for a in answers):
        return False

    return True


def describe_validation_failure(raw: Dict[str, Any]) -> str:
    """Explica por que uma pergunta foi descartada, pra facilitar o debug no log do Actions."""
    answers = raw.get("answers", [])
    if len(answers) != 4:
        return f"tem {len(answers)} alternativas, precisa ser 4"
    correct = [a for a in answers if a.get("isCorrect")]
    if len(correct) != 1:
        return f"tem {len(correct)} alternativas corretas, precisa ser exatamente 1"
    if not raw.get("prompt") or not raw.get("explanation"):
        return "faltando prompt ou explanation"
    if len(raw.get("prompt", "")) > MAX_PROMPT_CHARS:
        return f"pergunta muito longa ({len(raw['prompt'])} > {MAX_PROMPT_CHARS} caracteres)"
    if len(raw.get("explanation", "")) > MAX_EXPLANATION_CHARS:
        return f"explicação muito longa ({len(raw['explanation'])} > {MAX_EXPLANATION_CHARS} caracteres)"
    long_answer = next((a for a in answers if len(a.get("text", "")) > MAX_ANSWER_CHARS), None)
    if long_answer:
        return f"alternativa muito longa ({len(long_answer.get('text', ''))} > {MAX_ANSWER_CHARS} caracteres)"
    return "formato inválido"


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
            reason = describe_validation_failure(raw)
            print(f"  ⚠️  Pergunta descartada ({reason}): {raw.get('prompt', '???')[:60]}")
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
