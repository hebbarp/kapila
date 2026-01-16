# -*- coding: utf-8 -*-
"""
Kapila Keyword Mappings
=======================

EDUCATIONAL NOTE: Keywords vs Identifiers
-----------------------------------------

Keywords are reserved words that have special meaning in the language.
You can't use them as variable names.

In Kapila:
    ಸಂಖ್ಯೆ x = ೧೦    # ✓ x is an identifier
    ಸಂಖ್ಯೆ ಸಂಖ್ಯೆ = ೧೦  # ✗ can't use keyword as variable name

The lexer handles this by:
1. Reading a word (sequence of letters)
2. Looking it up in the KEYWORDS dictionary
3. If found → return keyword token
4. If not found → return identifier token

This is called "keyword identification" or "reserved word lookup".
"""

from .tokens import TokenType


# =============================================================================
# KANNADA KEYWORDS
# =============================================================================

KEYWORDS = {
    # Function-related
    'ಕಾರ್ಯ': TokenType.KARYA,              # function
    'ಹಿಂತಿರುಗಿಸು': TokenType.HINDIRUGISU,  # return

    # Control flow
    'ಆದರೆ': TokenType.ADARE,                # if
    'ಇಲ್ಲದಿದ್ದರೆ': TokenType.ILLADIDDARE,  # else
    'ತನಕ': TokenType.TANAKA,                # while/until
    'ಪುನರಾವರ್ತಿಸು': TokenType.PUNARAAVARTISU,  # repeat/loop
    'ಪ್ರತಿಯೊಂದಕ್ಕೂ': TokenType.PRATIYONDAKKU,  # for each
    'ನಿಲ್ಲಿಸು': TokenType.NILLISU,          # break
    'ಮುಂದುವರಿಸು': TokenType.MUNDUVARISU,    # continue

    # Type keywords
    'ಸಂಖ್ಯೆ': TokenType.SANKHYE,            # number
    'ಪೂರ್ಣಾಂಕ': TokenType.PURNANKA,        # integer
    'ದಶಮಾಂಶ': TokenType.DASHAMANSHA,       # decimal/float
    'ಪಠ್ಯ': TokenType.PATHYA,               # text/string
    'ಅಕ್ಷರ': TokenType.AKSHARA,             # character
    'ಪಟ್ಟಿ': TokenType.PATTI,               # list/array
    'ಶೂನ್ಯ': TokenType.SHUNYA,              # void/nothing

    # Boolean literals
    'ನಿಜ': TokenType.TRUE,                  # true
    'ಸುಳ್ಳು': TokenType.FALSE,              # false

    # Logical operators (word form)
    'ಮತ್ತು': TokenType.MATTU,               # and
    'ಅಥವಾ': TokenType.ATHAVA,              # or
    'ಅಲ್ಲ': TokenType.ALLA,                 # not

    # Other keywords
    'ಇರಲಿ': TokenType.IRALI,                # let (variable declaration)
    'ಮುದ್ರಿಸು': TokenType.MUDHRISU,         # print
}


def lookup_identifier(name: str) -> TokenType:
    """
    Look up a word in the keywords table.

    Returns the keyword TokenType if it's a reserved word,
    otherwise returns IDENTIFIER.

    EDUCATIONAL NOTE:
    This is where keywords become special. Without this lookup,
    'ಕಾರ್ಯ' would just be another identifier like 'x' or 'ಮುಖ್ಯ'.

    Example:
        lookup_identifier('ಕಾರ್ಯ')  # → TokenType.KARYA
        lookup_identifier('ಮುಖ್ಯ')  # → TokenType.IDENTIFIER
        lookup_identifier('x')     # → TokenType.IDENTIFIER
    """
    return KEYWORDS.get(name, TokenType.IDENTIFIER)


# =============================================================================
# KEYWORD INFORMATION (for documentation/tooling)
# =============================================================================

KEYWORD_INFO = {
    'ಕಾರ್ಯ': {
        'english': 'function',
        'meaning': 'Defines a function',
        'example': 'ಕಾರ್ಯ ಮುಖ್ಯ() { }',
    },
    'ಹಿಂತಿರುಗಿಸು': {
        'english': 'return',
        'meaning': 'Return a value from a function',
        'example': 'ಹಿಂತಿರುಗಿಸು ೧೦',
    },
    'ಆದರೆ': {
        'english': 'if',
        'meaning': 'Conditional execution',
        'example': 'ಆದರೆ (x > ೦) { }',
    },
    'ಇಲ್ಲದಿದ್ದರೆ': {
        'english': 'else',
        'meaning': 'Alternative branch',
        'example': 'ಇಲ್ಲದಿದ್ದರೆ { }',
    },
    'ತನಕ': {
        'english': 'while/until',
        'meaning': 'Loop while condition is true',
        'example': 'ತನಕ (x > ೦) { }',
    },
    'ಸಂಖ್ಯೆ': {
        'english': 'number',
        'meaning': 'Numeric type (integer or float)',
        'example': 'ಸಂಖ್ಯೆ x = ೧೦',
    },
    'ಪಠ್ಯ': {
        'english': 'text/string',
        'meaning': 'Text string type',
        'example': 'ಪಠ್ಯ s = "ನಮಸ್ಕಾರ"',
    },
    'ನಿಜ': {
        'english': 'true',
        'meaning': 'Boolean true value',
        'example': 'ಆದರೆ (ನಿಜ) { }',
    },
    'ಸುಳ್ಳು': {
        'english': 'false',
        'meaning': 'Boolean false value',
        'example': 'ಆದರೆ (ಸುಳ್ಳು) { }',
    },
    'ಮುದ್ರಿಸು': {
        'english': 'print',
        'meaning': 'Output to console',
        'example': 'ಮುದ್ರಿಸು("ನಮಸ್ಕಾರ")',
    },
}


def get_keyword_help(keyword: str) -> dict:
    """Get help information for a keyword."""
    return KEYWORD_INFO.get(keyword, {})


def list_all_keywords() -> list:
    """Return all keywords sorted alphabetically."""
    return sorted(KEYWORDS.keys())


if __name__ == "__main__":
    print("Kapila Keywords")
    print("=" * 60)
    print()

    for kw in list_all_keywords():
        info = get_keyword_help(kw)
        english = info.get('english', '?')
        print(f"  {kw:20} → {english}")
