# -*- coding: utf-8 -*-
"""
Vibhakti (ವಿಭಕ್ತಿ) — Kannada Case-Suffix Analyzer
====================================================

Decomposes Kannada words into stem + semantic role by stripping
vibhakti (case) suffixes. Ordered by longest suffix first to avoid
partial matches.

Roles:
    ವಸ್ತು   (object)    — ವನ್ನು / ಅನ್ನು / ನ್ನು
    ಗಮ್ಯ   (recipient) — ನಿಗೆ / ಕ್ಕೆ / ಗೆ
    ಸಾಧನ   (instrument) — ನಿಂದ / ಇಂದ
    ಸ್ಥಳ    (location)  — ನಲ್ಲಿ / ಅಲ್ಲಿ
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class VibhaktiResult:
    """Result of vibhakti analysis."""
    stem: str
    role: Optional[str]  # None means no vibhakti detected


# Suffixes ordered longest-first to prevent partial matches.
# Each entry: (suffix, role)
VIBHAKTI_SUFFIXES = [
    # Object (dvitiya vibhakti) — ವಸ್ತು
    ('ವನ್ನು', 'ವಸ್ತು'),
    ('ಅನ್ನು', 'ವಸ್ತು'),
    ('ನ್ನು',  'ವಸ್ತು'),

    # Recipient (chaturthi vibhakti) — ಗಮ್ಯ
    ('ನಿಗೆ',  'ಗಮ್ಯ'),
    ('ಕ್ಕೆ',   'ಗಮ್ಯ'),
    ('ಗೆ',    'ಗಮ್ಯ'),

    # Instrument (tritiya vibhakti) — ಸಾಧನ
    ('ನಿಂದ',  'ಸಾಧನ'),
    ('ಇಂದ',   'ಸಾಧನ'),

    # Location (saptami vibhakti) — ಸ್ಥಳ
    ('ನಲ್ಲಿ',  'ಸ್ಥಳ'),
    ('ಅಲ್ಲಿ',  'ಸ್ಥಳ'),
]


def normalize_stem(stem: str) -> str:
    """Normalize a stem after suffix removal.

    Strips zero-width non-joiner (U+200C) that Kannada text often
    inserts before suffixes (e.g. ಸರ್ವರ್\u200cನಲ್ಲಿ → ಸರ್ವರ್).
    """
    return stem.rstrip('\u200c').strip()


def analyze_vibhakti(word: str, known_words: frozenset) -> VibhaktiResult:
    """Analyze a Kannada word for vibhakti suffixes.

    Args:
        word: The word to analyze.
        known_words: Set of known builtins/vocabulary/keywords.
                     If the word is in this set, skip decomposition
                     to prevent false positives.

    Returns:
        VibhaktiResult with stem and detected role (or None).
    """
    # Guard: don't decompose known words
    if word in known_words:
        return VibhaktiResult(stem=word, role=None)

    for suffix, role in VIBHAKTI_SUFFIXES:
        if word.endswith(suffix) and len(word) > len(suffix):
            stem = normalize_stem(word[:-len(suffix)])
            if stem:
                return VibhaktiResult(stem=stem, role=role)

    return VibhaktiResult(stem=word, role=None)
