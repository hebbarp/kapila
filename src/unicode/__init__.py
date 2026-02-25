# -*- coding: utf-8 -*-
"""
Kapila Unicode Support
======================

Supports Kannada, Hindi (Devanagari), and Telugu — all Brahmic scripts
with identical Unicode layout, just different base offsets.
"""

from .kannada import (
    KANNADA_RANGE,
    is_kannada_char,
    is_kannada_letter,
    is_kannada_digit,
    kannada_digit_value,
)
from .kannada import (
    is_valid_identifier_start as _kn_id_start,
    is_valid_identifier_char as _kn_id_char,
)

from .hindi import (
    HINDI_RANGE,
    is_hindi_char,
    is_hindi_letter,
    is_hindi_digit,
    hindi_digit_value,
)
from .hindi import (
    is_valid_identifier_start as _hi_id_start,
    is_valid_identifier_char as _hi_id_char,
)

from .telugu import (
    TELUGU_RANGE,
    is_telugu_char,
    is_telugu_letter,
    is_telugu_digit,
    telugu_digit_value,
)
from .telugu import (
    is_valid_identifier_start as _te_id_start,
    is_valid_identifier_char as _te_id_char,
)


# =============================================================================
# UNIFIED FUNCTIONS — work for all scripts
# =============================================================================

def is_indic_char(ch: str) -> bool:
    return is_kannada_char(ch) or is_hindi_char(ch) or is_telugu_char(ch)


def is_indic_digit(ch: str) -> bool:
    return is_kannada_digit(ch) or is_hindi_digit(ch) or is_telugu_digit(ch)


def indic_digit_value(ch: str):
    v = kannada_digit_value(ch)
    if v is not None:
        return v
    v = hindi_digit_value(ch)
    if v is not None:
        return v
    return telugu_digit_value(ch)


def is_valid_identifier_start(ch: str) -> bool:
    return _kn_id_start(ch) or _hi_id_start(ch) or _te_id_start(ch)


def is_valid_identifier_char(ch: str) -> bool:
    return _kn_id_char(ch) or _hi_id_char(ch) or _te_id_char(ch)


__all__ = [
    # Kannada
    'KANNADA_RANGE', 'is_kannada_char', 'is_kannada_letter',
    'is_kannada_digit', 'kannada_digit_value',
    # Hindi
    'HINDI_RANGE', 'is_hindi_char', 'is_hindi_letter',
    'is_hindi_digit', 'hindi_digit_value',
    # Telugu
    'TELUGU_RANGE', 'is_telugu_char', 'is_telugu_letter',
    'is_telugu_digit', 'telugu_digit_value',
    # Unified
    'is_indic_char', 'is_indic_digit', 'indic_digit_value',
    'is_valid_identifier_start', 'is_valid_identifier_char',
]
