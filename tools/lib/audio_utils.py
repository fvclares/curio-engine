"""Audio post-processing helpers: resampling, normalization, padding, saving.

Kept independent from any specific TTS engine so it can be reused by future
generators (e.g. a narration track mixed for VideoGenerator) without any
coupling to Kokoro.
"""

from __future__ import annotations

from math import gcd
from pathlib import Path

import numpy as np
import soundfile as sf

#: The project standardizes on 44.1 kHz for every narration file.
TARGET_SAMPLE_RATE = 44100


def resample(audio: np.ndarray, original_sr: int, target_sr: int = TARGET_SAMPLE_RATE) -> np.ndarray:
    """Resamples ``audio`` from ``original_sr`` to ``target_sr`` (default 44.1 kHz)."""
    if original_sr == target_sr:
        return audio.astype(np.float32)

    from scipy.signal import resample_poly

    divisor = gcd(original_sr, target_sr)
    up, down = target_sr // divisor, original_sr // divisor
    return resample_poly(audio, up, down).astype(np.float32)


def normalize_peak(audio: np.ndarray, target_dbfs: float = -3.0) -> np.ndarray:
    """Scales ``audio`` so its peak sits at ``target_dbfs`` (default -3 dBFS).

    Peak normalization keeps every generated file at a consistent, safe
    volume without introducing the pumping artifacts that RMS/loudness
    normalization can cause on short speech clips.
    """
    peak = np.max(np.abs(audio)) if audio.size else 0.0
    if peak == 0:
        return audio.astype(np.float32)

    target_amplitude = 10 ** (target_dbfs / 20)
    return (audio * (target_amplitude / peak)).astype(np.float32)


def add_padding(audio: np.ndarray, sample_rate: int, lead_ms: int = 150, tail_ms: int = 350) -> np.ndarray:
    """Adds short silence before/after the clip for a natural, non-abrupt playback.

    A slightly longer tail than lead gives the narration room to "land"
    before the quiz UI advances to the next state.
    """
    lead = np.zeros(int(sample_rate * lead_ms / 1000), dtype=np.float32)
    tail = np.zeros(int(sample_rate * tail_ms / 1000), dtype=np.float32)
    return np.concatenate([lead, audio.astype(np.float32), tail])


def save_wav(path: Path, audio: np.ndarray, sample_rate: int = TARGET_SAMPLE_RATE) -> None:
    """Writes ``audio`` to ``path`` as 16-bit PCM WAV at ``sample_rate``."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), audio, sample_rate, subtype="PCM_16")
