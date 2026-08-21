"""AudioGenerator: generates narration WAV files for every question.

For each question in ``questions.json`` this produces up to three files:

  {id}-question.wav      narration of ``question["prompt"]``
  {id}-answer.wav         narration of the correct answer's text
  {id}-explanation.wav    narration of ``question["explanation"]``

and writes the matching ``questionAudio`` / ``answerAudio`` /
``explanationAudio`` keys back into the question so the front-end knows
which file to play.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .audio_utils import (
    TARGET_SAMPLE_RATE,
    add_padding,
    normalize_peak,
    resample,
    save_wav,
)
from .base_generator import AssetSpec, BaseGenerator, QuestionRepository
from .kokoro_backend import DEFAULT_LANG_CODE, DEFAULT_VOICE, KOKORO_SAMPLE_RATE, KokoroBackend
from .text_processing import preprocess

# (asset_type, json_key, log_label)
_ASSET_TYPES = (
    ("question", "questionAudio", "pergunta"),
    ("answer", "answerAudio", "resposta"),
    ("explanation", "explanationAudio", "explicação"),
)


def _correct_answer_text(question: Dict[str, Any]) -> str:
    for answer in question.get("answers", []):
        if answer.get("isCorrect"):
            return answer.get("text", "")
    return ""


def _text_for_asset(question: Dict[str, Any], asset_type: str) -> str:
    if asset_type == "question":
        return question.get("prompt", "")
    if asset_type == "answer":
        return _correct_answer_text(question)
    if asset_type == "explanation":
        return question.get("explanation", "")
    raise ValueError(f"Tipo de asset de áudio desconhecido: {asset_type}")


class AudioGenerator(BaseGenerator):
    """Generates question/answer/explanation narration with Kokoro TTS."""

    label = "audio"

    def __init__(
        self,
        repository: QuestionRepository,
        output_dir: Path,
        force: bool = False,
        voice: str = DEFAULT_VOICE,
        lang_code: str = DEFAULT_LANG_CODE,
        speed: float = 0.9,
    ) -> None:
        super().__init__(repository, force=force)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._voice = voice
        self._lang_code = lang_code
        self._speed = speed
        self._backend: Optional[KokoroBackend] = None

    @property
    def backend(self) -> KokoroBackend:
        """Lazily creates the Kokoro backend (only once, only if needed).

        This means listing/checking existing files never requires Kokoro
        (and its model download) to be available at all.
        """
        if self._backend is None:
            self._backend = KokoroBackend(
                lang_code=self._lang_code, voice=self._voice, speed=self._speed
            )
        return self._backend

    def asset_specs(self, question: Dict[str, Any]) -> List[AssetSpec]:
        qid = question.get("id", "unknown")
        specs = []

        for asset_type, json_key, log_label in _ASSET_TYPES:
            text = _text_for_asset(question, asset_type)
            filename = f"{qid}-{asset_type}.wav"
            specs.append(
                AssetSpec(
                    label=log_label,
                    json_key=json_key,
                    output_path=self.output_dir / filename,
                    relative_path=f"assets/audio/{filename}",
                    text=text,
                )
            )

        return specs

    def generate_asset(self, question: Dict[str, Any], spec: AssetSpec) -> None:
        if not spec.text or not spec.text.strip():
            raise ValueError("texto vazio para narrar")

        text = preprocess(spec.text)
        waveform = self.backend.synthesize(text)
        waveform = resample(waveform, KOKORO_SAMPLE_RATE, TARGET_SAMPLE_RATE)
        waveform = normalize_peak(waveform)
        waveform = add_padding(waveform, TARGET_SAMPLE_RATE)
        save_wav(spec.output_path, waveform, TARGET_SAMPLE_RATE)
