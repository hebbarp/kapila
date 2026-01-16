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
    PIPE = auto()            # |  (block parameter separator)

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
