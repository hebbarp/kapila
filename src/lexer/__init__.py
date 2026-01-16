# -*- coding: utf-8 -*-
"""
Kapila Lexer Module
===================

Tokenizes Kapila source code.

Usage:
    from kapila.lexer import tokenize, Lexer, Token, TokenType

    tokens = tokenize('೫ + ೧೦ ಮುದ್ರಿಸು.')
"""

from .tokens import Token, TokenType
from .lexer import Lexer, tokenize

__all__ = [
    'Lexer',
    'Token',
    'TokenType',
    'tokenize',
]
