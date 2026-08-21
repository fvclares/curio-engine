"""Thin wrapper around the local Kokoro TTS engine.

Isolating the Kokoro-specific API here means the rest of the pipeline
(``AudioGenerator``, ``audio_utils``, ``text_processing``) never imports
``kokoro`` directly, so swapping the TTS engine later only means rewriting
this one file.

Kokoro model & voice weights are downloaded automatically (and cached) by
the ``kokoro`` package the first time ``KPipeline`` is instantiated - see
``tools/README.md`` for how that download works and how to pre-fetch it.
"""

from __future__ import annotations

import numpy as np

#: Kokoro always renders audio at 24 kHz internally.
KOKORO_SAMPLE_RATE = 24000

#: Portuguese (Brazil) voices bundled with Kokoro >= 1.0.
#: pf_dora  = feminine voice (project default)
#: pm_alex / pm_santa = masculine voices
DEFAULT_VOICE = "pf_dora"
DEFAULT_LANG_CODE = "p"  # 'p' = Portuguese (Brazil) in Kokoro's misaki front-end


class KokoroBackend:
    """Lazily loads Kokoro and synthesizes text into a mono float32 waveform."""

    def __init__(
        self,
        lang_code: str = DEFAULT_LANG_CODE,
        voice: str = DEFAULT_VOICE,
        speed: float = 0.9,
    ) -> None:
        try:
            from kokoro import KPipeline
        except ImportError as exc:
            raise RuntimeError(
                "O pacote 'kokoro' não está instalado.\n"
                "Rode: pip install -r tools/requirements.txt\n"
                "Consulte tools/README.md para o passo a passo completo."
            ) from exc

        self.voice = voice
        self.speed = speed

        try:
            self.pipeline = KPipeline(lang_code=lang_code)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(
                "Falha ao inicializar o Kokoro (KPipeline). Isso geralmente "
                "significa que o modelo ainda não foi baixado ou que o "
                "'espeak-ng' não está instalado/no PATH. "
                "Consulte tools/README.md, seção 'Baixar o modelo Kokoro'."
            ) from exc

    def synthesize(self, text: str) -> np.ndarray:
        """Synthesizes ``text`` and returns a mono float32 waveform at 24 kHz."""
        chunks = []
        for _graphemes, _phonemes, audio in self.pipeline(text, voice=self.voice, speed=self.speed):
            chunks.append(np.asarray(audio, dtype=np.float32))

        if not chunks:
            raise RuntimeError("Kokoro não retornou nenhum áudio para o texto fornecido.")

        return np.concatenate(chunks)
