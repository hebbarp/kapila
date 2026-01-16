# -*- coding: utf-8 -*-
"""
Kapila Unicode Support
======================

This module provides Kannada script handling for the Kapila compiler.
Adapted from Pampa: AdiLipi project.

Understanding Unicode for Kannada:
---------------------------------
Kannada uses Unicode block U+0C80 to U+0CFF (128 codepoints).

Key concepts:
- Vowels (ಸ್ವರಗಳು): ಅ ಆ ಇ ಈ ಉ ಊ...
- Consonants (ವ್ಯಂಜನಗಳು): ಕ ಖ ಗ ಘ...
- Matras (dependent vowels): ಾ ಿ ೀ ು ೂ...
- Halant/Virama (್): Kills the inherent 'a' vowel
- Anusvara (ಂ): Nasalization
- Visarga (ಃ): Aspiration

For a programming language, we need to:
1. Identify valid identifier characters
2. Recognize Kannada numerals (೦-೯)
3. Handle conjuncts in identifiers (like ಸ್ಕ in ನಮಸ್ಕಾರ)
"""

from .kannada import (
    KANNADA_RANGE,
    is_kannada_char,
    is_kannada_letter,
    is_kannada_digit,
    is_valid_identifier_start,
    is_valid_identifier_char,
    kannada_digit_value,
)

__all__ = [
    'KANNADA_RANGE',
    'is_kannada_char',
    'is_kannada_letter',
    'is_kannada_digit',
    'is_valid_identifier_start',
    'is_valid_identifier_char',
    'kannada_digit_value',
]
