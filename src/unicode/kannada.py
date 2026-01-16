# -*- coding: utf-8 -*-
"""
Kannada Unicode Handling for Kapila
===================================

EDUCATIONAL NOTE: Understanding Unicode
---------------------------------------

Unicode assigns every character a unique number called a "codepoint".
In Python, ord('ಕ') gives you 0x0C95 (3221 in decimal).
chr(0x0C95) gives you 'ಕ'.

Kannada occupies codepoints U+0C80 to U+0CFF.
This is a "block" of 128 positions, though not all are used.

The Brahmic Script Pattern:
--------------------------
All Indian scripts (Devanagari, Tamil, Telugu, Kannada, etc.) follow
a similar pattern in Unicode. If you know the base offset, you can
calculate character positions:

    Base (Kannada) = 0x0C80

    Anusvara  = Base + 0x02 = 0x0C82 = ಂ
    Visarga   = Base + 0x03 = 0x0C83 = ಃ
    Vowel 'ಅ' = Base + 0x05 = 0x0C85 = ಅ
    Consonant 'ಕ' = Base + 0x15 = 0x0C95 = ಕ
    Halant    = Base + 0x4D = 0x0CCD = ್

This regularity is why we can write generic code for multiple scripts!

For Kapila Compiler:
-------------------
We need to answer these questions:
1. Is this character Kannada? (for lexer to know when identifier ends)
2. Is this a valid identifier start? (letters, not numbers)
3. Is this a valid identifier continuation? (letters, numbers, matras)
4. Is this a Kannada digit? (೦-೯)

Adapted from Pampa: AdiLipi project.
"""

from typing import Optional


# =============================================================================
# KANNADA UNICODE RANGE
# =============================================================================

KANNADA_RANGE = (0x0C80, 0x0CFF)

# Base offset for calculating positions
_BASE = 0x0C80


# =============================================================================
# CHARACTER SETS
# =============================================================================

# Kannada digits: ೦ ೧ ೨ ೩ ೪ ೫ ೬ ೭ ೮ ೯
# These are at positions Base + 0x66 to Base + 0x6F
KANNADA_DIGITS = {chr(_BASE + 0x66 + i) for i in range(10)}
# That's: {'೦', '೧', '೨', '೩', '೪', '೫', '೬', '೭', '೮', '೯'}

# Map Kannada digits to their integer values
DIGIT_VALUES = {chr(_BASE + 0x66 + i): i for i in range(10)}
# {'೦': 0, '೧': 1, '೨': 2, ...}

# Special characters
ANUSVARA = chr(_BASE + 0x02)   # ಂ - nasalization mark
VISARGA = chr(_BASE + 0x03)    # ಃ - aspiration mark
HALANT = chr(_BASE + 0x4D)     # ್ - vowel killer (virama)

# Independent vowels: ಅ ಆ ಇ ಈ ಉ ಊ ಋ ೠ ಎ ಏ ಐ ಒ ಓ ಔ
# Positions: 0x05-0x14 (with some gaps)
VOWELS_INDEPENDENT = set()
for offset in [0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C,
               0x0E, 0x0F, 0x10, 0x12, 0x13, 0x14]:
    VOWELS_INDEPENDENT.add(chr(_BASE + offset))

# Dependent vowels (matras): ಾ ಿ ೀ ು ೂ ೃ ೄ ೆ ೇ ೈ ೊ ೋ ೌ
# These attach to consonants: ಕ + ಾ = ಕಾ
# Positions: 0x3E-0x4C (with some gaps)
MATRAS = set()
for offset in [0x3E, 0x3F, 0x40, 0x41, 0x42, 0x43, 0x44,
               0x46, 0x47, 0x48, 0x4A, 0x4B, 0x4C]:
    MATRAS.add(chr(_BASE + offset))

# Consonants: ಕ ಖ ಗ ಘ ಙ ಚ ಛ ಜ ಝ ಞ ಟ ಠ ಡ ಢ ಣ ತ ಥ ದ ಧ ನ ಪ ಫ ಬ ಭ ಮ ಯ ರ ಱ ಲ ವ ಶ ಷ ಸ ಹ ಳ
# Positions: 0x15-0x39
CONSONANTS = {chr(_BASE + offset) for offset in range(0x15, 0x3A)}

# All letters (for identifier purposes)
LETTERS = VOWELS_INDEPENDENT | CONSONANTS


# =============================================================================
# CHARACTER CLASSIFICATION FUNCTIONS
# =============================================================================

def is_kannada_char(ch: str) -> bool:
    """
    Check if a character is in the Kannada Unicode block.

    EDUCATIONAL NOTE:
    This is the most basic check - just "is it in the range?"
    We use this to know when we've left Kannada text.

    Example:
        is_kannada_char('ಕ')  # True
        is_kannada_char('a')  # False
        is_kannada_char('क')  # False (that's Hindi!)
    """
    if not ch:
        return False
    cp = ord(ch[0])
    return KANNADA_RANGE[0] <= cp <= KANNADA_RANGE[1]


def is_kannada_letter(ch: str) -> bool:
    """
    Check if character is a Kannada letter (vowel or consonant).

    EDUCATIONAL NOTE:
    Not all Kannada characters are "letters". Digits, matras,
    and punctuation are in the block but aren't letters.

    For identifiers, we want actual letters that can start a word.
    """
    return ch in LETTERS


def is_kannada_digit(ch: str) -> bool:
    """
    Check if character is a Kannada digit (೦-೯).

    EDUCATIONAL NOTE:
    Kannada has its own numerals! They're rarely used in modern
    writing (Arabic numerals dominate), but Kapila should support them.

    ೦=0, ೧=1, ೨=2, ೩=3, ೪=4, ೫=5, ೬=6, ೭=7, ೮=8, ೯=9
    """
    return ch in KANNADA_DIGITS


def kannada_digit_value(ch: str) -> Optional[int]:
    """
    Get the numeric value of a Kannada digit.

    Returns None if not a Kannada digit.

    Example:
        kannada_digit_value('೫')  # 5
        kannada_digit_value('5')  # None (ASCII digit)
    """
    return DIGIT_VALUES.get(ch)


def is_valid_identifier_start(ch: str) -> bool:
    """
    Check if character can START a Kapila identifier.

    EDUCATIONAL NOTE:
    In most languages, identifiers can't start with digits.
    We follow the same rule: letters only.

    Valid starts: ಕ, ಅ, ಮ, etc.
    Invalid starts: ೧, ್, ಾ
    """
    return ch in LETTERS


def is_valid_identifier_char(ch: str) -> bool:
    """
    Check if character can CONTINUE a Kapila identifier.

    EDUCATIONAL NOTE:
    After the first character, identifiers can include:
    - More letters (ಕ, ಅ, etc.)
    - Digits (೦-೯ and 0-9)
    - Matras (ಾ, ಿ, etc.) - these attach to consonants
    - Halant (್) - for conjuncts like ಸ್ಕ
    - Anusvara (ಂ) and Visarga (ಃ)

    This allows natural Kannada words as identifiers:
    - ಸಂಖ್ಯೆ (number) - has anusvara and halant
    - ಮುದ್ರಿಸು (print) - has halant for conjunct
    """
    if not ch:
        return False

    # Letters are always valid
    if ch in LETTERS:
        return True

    # Kannada digits
    if ch in KANNADA_DIGITS:
        return True

    # ASCII digits (for convenience)
    if ch.isdigit():
        return True

    # Matras (dependent vowels)
    if ch in MATRAS:
        return True

    # Halant (for conjuncts)
    if ch == HALANT:
        return True

    # Anusvara and Visarga
    if ch in (ANUSVARA, VISARGA):
        return True

    # Underscore (common in programming)
    if ch == '_':
        return True

    return False


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def parse_kannada_number(text: str) -> Optional[int]:
    """
    Parse a string of Kannada digits into an integer.

    EDUCATIONAL NOTE:
    This handles numbers written in Kannada numerals.
    ೧೨೩ → 123

    We'll use this in the lexer when we see Kannada digits.
    """
    if not text:
        return None

    result = 0
    for ch in text:
        value = kannada_digit_value(ch)
        if value is None:
            return None
        result = result * 10 + value

    return result


def normalize_number(text: str) -> Optional[int]:
    """
    Parse either Kannada or ASCII digits into an integer.

    Supports: "123", "೧೨೩", or mixed "೧2೩"
    """
    if not text:
        return None

    result = 0
    for ch in text:
        # Try Kannada digit first
        value = kannada_digit_value(ch)
        if value is not None:
            result = result * 10 + value
            continue

        # Try ASCII digit
        if ch.isdigit():
            result = result * 10 + int(ch)
            continue

        # Invalid character
        return None

    return result


# =============================================================================
# DEMONSTRATION
# =============================================================================

if __name__ == "__main__":
    print("Kapila Kannada Unicode Support")
    print("=" * 50)

    # Show character classifications
    test_chars = ['ಕ', 'ಅ', '್', 'ಾ', 'ಂ', '೫', 'a', '5']

    print("\nCharacter Classification:")
    print("-" * 50)
    for ch in test_chars:
        print(f"  '{ch}' (U+{ord(ch):04X}):")
        print(f"      is_kannada_char: {is_kannada_char(ch)}")
        print(f"      is_kannada_letter: {is_kannada_letter(ch)}")
        print(f"      is_kannada_digit: {is_kannada_digit(ch)}")
        print(f"      is_valid_identifier_start: {is_valid_identifier_start(ch)}")
        print(f"      is_valid_identifier_char: {is_valid_identifier_char(ch)}")

    # Test identifier validation
    print("\nIdentifier Examples:")
    print("-" * 50)
    identifiers = ['ಸಂಖ್ಯೆ', 'ಮುದ್ರಿಸು', 'x೧', '೧x', 'ಕಾರ್ಯ']
    for ident in identifiers:
        valid_start = is_valid_identifier_start(ident[0]) if ident else False
        valid_rest = all(is_valid_identifier_char(c) for c in ident[1:]) if len(ident) > 1 else True
        valid = valid_start and valid_rest
        print(f"  '{ident}': {'valid' if valid else 'invalid'}")

    # Test number parsing
    print("\nNumber Parsing:")
    print("-" * 50)
    numbers = ['೧೨೩', '42', '೪2', '']
    for num in numbers:
        result = normalize_number(num)
        print(f"  '{num}' → {result}")
