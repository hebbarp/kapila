# -*- coding: utf-8 -*-
"""
Telugu Unicode Handling for Kapila
==================================

Same Brahmic pattern as Kannada and Hindi — just shift the base:
    Kannada base    = 0x0C80
    Devanagari base = 0x0900
    Telugu base     = 0x0C00

Every offset is identical:
    Digits:     base + 0x66  (౦-౯)
    Consonants: base + 0x15 to base + 0x39  (క-హ)
    Vowels:     base + 0x05 to base + 0x14  (అ-ఔ)
    Halant:     base + 0x4D  (్)
    Anusvara:   base + 0x02  (ం)
    Visarga:    base + 0x03  (ః)
"""

from typing import Optional


# =============================================================================
# TELUGU UNICODE RANGE
# =============================================================================

TELUGU_RANGE = (0x0C00, 0x0C7F)

_BASE = 0x0C00

# =============================================================================
# CHARACTER SETS
# =============================================================================

# Telugu digits: ౦ ౧ ౨ ౩ ౪ ౫ ౬ ౭ ౮ ౯
TELUGU_DIGITS = {chr(_BASE + 0x66 + i) for i in range(10)}

DIGIT_VALUES = {chr(_BASE + 0x66 + i): i for i in range(10)}

# Special characters
ANUSVARA = chr(_BASE + 0x02)   # ం
VISARGA = chr(_BASE + 0x03)    # ః
HALANT = chr(_BASE + 0x4D)     # ్

# Independent vowels: అ ఆ ఇ ఈ ఉ ఊ ఋ ౠ ఎ ఏ ఐ ఒ ఓ ఔ
VOWELS_INDEPENDENT = set()
for offset in [0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C,
               0x0E, 0x0F, 0x10, 0x12, 0x13, 0x14]:
    VOWELS_INDEPENDENT.add(chr(_BASE + offset))

# Dependent vowels (matras): ా ి ీ ు ూ ృ ౄ ె ే ై ొ ో ౌ
MATRAS = set()
for offset in [0x3E, 0x3F, 0x40, 0x41, 0x42, 0x43, 0x44,
               0x46, 0x47, 0x48, 0x4A, 0x4B, 0x4C]:
    MATRAS.add(chr(_BASE + offset))

# Consonants: క ఖ గ ఘ ఙ ... హ
CONSONANTS = {chr(_BASE + offset) for offset in range(0x15, 0x3A)}

# All letters
LETTERS = VOWELS_INDEPENDENT | CONSONANTS


# =============================================================================
# CHARACTER CLASSIFICATION FUNCTIONS
# =============================================================================

def is_telugu_char(ch: str) -> bool:
    if not ch:
        return False
    cp = ord(ch[0])
    return TELUGU_RANGE[0] <= cp <= TELUGU_RANGE[1]


def is_telugu_letter(ch: str) -> bool:
    return ch in LETTERS


def is_telugu_digit(ch: str) -> bool:
    return ch in TELUGU_DIGITS


def telugu_digit_value(ch: str) -> Optional[int]:
    return DIGIT_VALUES.get(ch)


def is_valid_identifier_start(ch: str) -> bool:
    return ch in LETTERS


def is_valid_identifier_char(ch: str) -> bool:
    if not ch:
        return False
    if ch in LETTERS:
        return True
    if ch in TELUGU_DIGITS:
        return True
    if ch.isdigit():
        return True
    if ch in MATRAS:
        return True
    if ch == HALANT:
        return True
    if ch in (ANUSVARA, VISARGA):
        return True
    if ch == '_':
        return True
    return False
