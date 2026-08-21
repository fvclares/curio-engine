"""Shared infrastructure for CurioEngine content generators.

This module holds the pieces that are common to *any* per-question asset
generator: loading/saving ``questions.json`` and iterating over the
question list while checking what already exists on disk.

The goal is that future generators (``ImageGenerator``,
``SubtitleGenerator``, ``VideoGenerator``, ...) can be written by only
implementing two small methods (``asset_specs`` and ``generate_asset``)
without ever touching ``AudioGenerator`` or duplicating its logic.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


class QuestionRepository:
    """Loads, mutates in-memory, and persists CurioEngine's ``questions.json``."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._questions: List[Dict[str, Any]] = []

    def load(self) -> List[Dict[str, Any]]:
        """Reads the JSON file into memory and returns the question list."""
        if not self.path.exists():
            raise FileNotFoundError(f"Arquivo de perguntas não encontrado: {self.path}")

        with self.path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)

        if not isinstance(data, list):
            raise ValueError(f"{self.path} deve conter um array JSON de perguntas.")

        self._questions = data
        return self._questions

    @property
    def questions(self) -> List[Dict[str, Any]]:
        """The in-memory list of questions (call ``load()`` first)."""
        return self._questions

    def save(self) -> None:
        """Writes the (possibly modified) in-memory questions back to disk."""
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(self._questions, fh, ensure_ascii=False, indent=2)
            fh.write("\n")


@dataclass
class AssetSpec:
    """Describes a single asset (file) a question needs.

    ``label`` and ``json_key`` are generic on purpose so this same dataclass
    can describe an audio file today and an image, subtitle, or video file
    tomorrow.
    """

    label: str            # Human label used in the progress log, e.g. "pergunta"
    json_key: str          # Key written back into questions.json, e.g. "questionAudio"
    output_path: Path      # Absolute path where the asset must be written
    relative_path: str     # Path stored in the JSON (relative to the project root)
    text: str = ""         # Source text to synthesize/render, when applicable
    extra: Dict[str, Any] = field(default_factory=dict)


class BaseGenerator(ABC):
    """Common skeleton for any per-question asset generator.

    Subclasses only need to implement:
      * ``asset_specs(question)`` -> which files should exist for this question
      * ``generate_asset(question, spec)`` -> how to actually create one file

    Everything else (iterating all questions, skipping files that already
    exist, printing progress, and saving the updated JSON) lives here.
    """

    #: Short label used in progress logs, e.g. "audio", "image", "subtitle"
    label: str = "asset"

    def __init__(self, repository: QuestionRepository, force: bool = False) -> None:
        self.repository = repository
        self.force = force

    @abstractmethod
    def asset_specs(self, question: Dict[str, Any]) -> List[AssetSpec]:
        """Returns the list of assets this generator must produce for a question."""

    @abstractmethod
    def generate_asset(self, question: Dict[str, Any], spec: AssetSpec) -> None:
        """Creates the asset described by ``spec`` on disk."""

    def run(self) -> None:
        """Iterates over every question, generating missing assets and saving."""
        questions = self.repository.questions
        total = len(questions)
        print(f"\n=== {self.label.upper()} GENERATOR - {total} pergunta(s) ===\n")

        had_error = False

        for index, question in enumerate(questions, start=1):
            qid = question.get("id", f"question-{index}")
            print(f"[{index}/{total}] {qid}")

            for spec in self.asset_specs(question):
                already_exists = spec.output_path.exists()

                if already_exists and not self.force:
                    print(f"  \u21b7 {spec.label} (já existe, pulando)")
                    question[spec.json_key] = spec.relative_path
                    continue

                try:
                    self.generate_asset(question, spec)
                    question[spec.json_key] = spec.relative_path
                    print(f"  \u2714 {spec.label}")
                except Exception as exc:  # noqa: BLE001 - report and keep going
                    had_error = True
                    print(f"  \u2716 {spec.label} - erro: {exc}")

        self.repository.save()

        status = "com erros" if had_error else "com sucesso"
        print(f"\n{self.label.capitalize()} concluído {status}. "
              f"{self.repository.path} atualizado.\n")
