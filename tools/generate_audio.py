#!/usr/bin/env python3
"""Gera a narração do CurioEngine em áudio, offline, usando Kokoro TTS.

Uso básico:

    pip install -r tools/requirements.txt
    python tools/generate_audio.py
    python tools/generate_audio.py --force

Veja tools/README.md para instruções completas de instalação.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Permite rodar "python tools/generate_audio.py" a partir de qualquer diretório.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.audio_generator import AudioGenerator  # noqa: E402
from lib.base_generator import QuestionRepository  # noqa: E402
from lib.kokoro_backend import DEFAULT_VOICE  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUESTIONS_PATH = PROJECT_ROOT / "data" / "questions.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "assets" / "audio"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera arquivos .wav de narração para o CurioEngine usando Kokoro TTS local."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenera todos os áudios, mesmo os que já existem.",
    )
    parser.add_argument(
        "--questions",
        default=str(DEFAULT_QUESTIONS_PATH),
        help=f"Caminho do questions.json (padrão: {DEFAULT_QUESTIONS_PATH})",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Pasta de saída dos áudios (padrão: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--voice",
        default=DEFAULT_VOICE,
        help=f"Voz do Kokoro a usar (padrão: {DEFAULT_VOICE}, feminina, pt-BR).",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=0.9,
        help="Velocidade da fala: 1.0 = normal, <1.0 = mais lento (padrão: 0.9).",
    )
    return parser.parse_args()


def clean_orphan_audios(repository: QuestionRepository, output_dir: Path) -> None:
    """Remove arquivos .wav da pasta de saída que não correspondem às perguntas ativas."""
    if not output_dir.exists():
        return

    # Coleta todos os caminhos esperados para as perguntas do arquivo JSON
    expected_files: set[Path] = set()
    for question in repository.questions:
        for key in ("questionAudio", "answerAudio", "explanationAudio"):
            audio_path_str = question.get(key)
            if audio_path_str:
                # Converte caminho relativo para o caminho absoluto no sistema de arquivos
                expected_files.add((PROJECT_ROOT / audio_path_str).resolve())

    # Varre a pasta de saída e apaga .wav que não estão na lista de esperados
    removed_count = 0
    for wav_file in output_dir.glob("*.wav"):
        if wav_file.resolve() not in expected_files:
            try:
                wav_file.unlink()
                removed_count += 1
            except OSError as exc:
                print(f"Aviso: Não foi possível remover áudio antigo {wav_file.name}: {exc}", file=sys.stderr)

    if removed_count > 0:
        print(f"🧹 Limpeza concluída: {removed_count} áudio(s) antigo(s) removido(s).")


def main() -> int:
    args = parse_args()

    try:
        repository = QuestionRepository(Path(args.questions))
        repository.load()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Erro ao carregar perguntas: {exc}", file=sys.stderr)
        return 1

    output_dir = Path(args.output)

    # Executa a limpeza dos áudios das perguntas que não existem mais no JSON
    clean_orphan_audios(repository, output_dir)

    generator = AudioGenerator(
        repository=repository,
        output_dir=output_dir,
        force=args.force,
        voice=args.voice,
        speed=args.speed,
    )

    try:
        generator.run()
    except RuntimeError as exc:
        # Erros de inicialização do Kokoro (modelo/backend ausente) já vêm
        # com uma mensagem explicativa de lib/kokoro_backend.py.
        print(f"\nErro fatal: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
