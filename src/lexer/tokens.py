# -*- coding: utf-8 -*-
"""
Kapila Token Definitions
========================

Kapila is a stack-based language with:
- Forth's concatenative core
- Smalltalk's message-passing readability
- Perl's pronouns (ಅದು, ನೀನು)
- Clojure's immutable data

Token types for the lexer.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional


class TokenType(Enum):
    """All token types in Kapila."""

    # Literals
    NUMBER = auto()          # ೧೨೩, 123, ೩.೧೪
    STRING = auto()          # "ನಮಸ್ಕಾರ"

    # Identifiers and Words
    WORD = auto()            # ಮುದ್ರಿಸು, ವರ್ಗ, x, ಅದು

    # Definition and Assignment
    COLON = auto()           # :  (word definition)
    ASSIGN = auto()          # := (value binding)
    DEF_END = auto()         # ॥  (definition end)

    # Delimiters
    DOT = auto()             # .  (statement end)
    LBRACKET = auto()        # [  (block start)
    RBRACKET = auto()        # ]  (block end)
    LBRACE = auto()          # {  (data structure start)
    RBRACE = auto()          # }  (data structure end)
    PIPE = auto()            # |  (block parameter separator - deprecated, use ->)
    ARROW = auto()           # -> (block parameter separator)

    # Quotation
    QUOTE = auto()           # '  (quote next word)
    QUESTION = auto()        # ?  (conditional)

    # Arithmetic Operators
    PLUS = auto()            # +
    MINUS = auto()           # -
    STAR = auto()            # *
    SLASH = auto()           # /
    PERCENT = auto()         # %

    # Comparison Operators
    EQ = auto()              # =
    NEQ = auto()             # ≠ or !=
    LT = auto()              # <
    GT = auto()              # >
    LTE = auto()             # ≤ or <=
    GTE = auto()             # ≥ or >=

    # Keywords (for procedural syntax)
    IDENTIFIER = auto()      # generic identifier
    KARYA = auto()           # ಕಾರ್ಯ (function)
    HINDIRUGISU = auto()     # ಹಿಂತಿರುಗಿಸು (return)
    ADARE = auto()           # ಆದರೆ (if)
    ILLADIDDARE = auto()     # ಇಲ್ಲದಿದ್ದರೆ (else)
    TANAKA = auto()          # ತನಕ (while)
    PUNARAAVARTISU = auto()  # ಪುನರಾವರ್ತಿಸು (loop)
    PRATIYONDAKKU = auto()   # ಪ್ರತಿಯೊಂದಕ್ಕೂ (for-each)
    NILLISU = auto()         # ನಿಲ್ಲಿಸು (break)
    MUNDUVARISU = auto()     # ಮುಂದುವರಿಸು (continue)
    SANKHYE = auto()         # ಸಂಖ್ಯೆ (number type)
    PURNANKA = auto()        # ಪೂರ್ಣಾಂಕ (integer type)
    DASHAMANSHA = auto()     # ದಶಮಾಂಶ (float type)
    PATHYA = auto()          # ಪಠ್ಯ (string type)
    AKSHARA = auto()         # ಅಕ್ಷರ (char type)
    PATTI = auto()           # ಪಟ್ಟಿ (list type)
    SHUNYA = auto()          # ಶೂನ್ಯ (void type)
    TRUE = auto()            # ನಿಜ (true)
    FALSE = auto()           # ಸುಳ್ಳು (false)
    MATTU = auto()           # ಮತ್ತು (and)
    ATHAVA = auto()          # ಅಥವಾ (or)
    ALLA = auto()            # ಅಲ್ಲ (not)
    IRALI = auto()           # ಇರಲಿ (let)
    MUDHRISU = auto()        # ಮುದ್ರಿಸು (print)

    # Special
    NEWLINE = auto()         # newline (may be significant)
    EOF = auto()             # end of file
    ERROR = auto()           # lexical error


@dataclass
class Token:
    """A single token from source code."""
    type: TokenType
    value: str
    line: int
    column: int
    literal: Optional[Any] = None

    def __repr__(self) -> str:
        if self.literal is not None:
            return f"Token({self.type.name}, {self.value!r}, ={self.literal})"
        return f"Token({self.type.name}, {self.value!r})"

    def __str__(self) -> str:
        return f"{self.type.name}({self.value!r})"
