"""Text pre-processing applied before sending text to Kokoro TTS.

Kokoro (like most TTS engines) reads punctuation as prosody: commas create
short pauses, sentence-ending punctuation creates longer ones. This module
normalizes whitespace, expands a few abbreviations that would otherwise be
mispronounced in Portuguese, and guarantees every text ends with proper
punctuation so Kokoro closes the sentence naturally instead of clipping it.
"""

from __future__ import annotations

import re

# Common abbreviations / symbols that Kokoro's Portuguese front-end tends to
# mispronounce or skip. Extend this table as new edge cases show up in the
# question bank.
_ABBREVIATIONS = {
    "km/h": "quilômetros por hora",
    "km²": "quilômetros quadrados",
    "m²": "metros quadrados",
    "Sr.": "Senhor",
    "Sra.": "Senhora",
    "Dr.": "Doutor",
    "Dra.": "Doutora",
    "°C": " graus Celsius",
    "%": " por cento",
}

_WHITESPACE_RE = re.compile(r"\s+")
_COMMA_RE = re.compile(r"\s*,\s*")
_SEMICOLON_RE = re.compile(r"\s*;\s*")


def preprocess(text: str) -> str:
    """Cleans and normalizes narration text before synthesis.

    - Expands abbreviations that would otherwise confuse the G2P step.
    - Collapses redundant whitespace.
    - Normalizes spacing around commas/semicolons so Kokoro renders a clear,
      short pause instead of running words together.
    - Ensures the text ends with sentence-ending punctuation, which gives a
      natural closing pause/intonation drop instead of an abrupt cut.
    """
    if not text:
        return text

    cleaned = text.strip()

    for abbreviation, expansion in _ABBREVIATIONS.items():
        cleaned = cleaned.replace(abbreviation, expansion)

    cleaned = _WHITESPACE_RE.sub(" ", cleaned)
    cleaned = _COMMA_RE.sub(", ", cleaned)
    cleaned = _SEMICOLON_RE.sub("; ", cleaned)
    cleaned = cleaned.strip()

    if cleaned and cleaned[-1] not in ".!?…":
        cleaned += "."

    return cleaned
