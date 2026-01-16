# -*- coding: utf-8 -*-
"""
ಕಪಿಲ (Kapila) - A Kannada Programming Language
===============================================

A stack-based language with:
- Forth's concatenative soul
- Smalltalk's message-passing face
- Perl's pronouns (ಅದು, ನೀನು)
- Clojure's immutable heart
- Infix math, postfix actions

Quick Start:
    from kapila import VM

    vm = VM()
    vm.run('"ನಮಸ್ಕಾರ ಜಗತ್ತು!" ಮುದ್ರಿಸು.')

Example:
    ವರ್ಗ: ನಕಲು * ॥
    ೫ ವರ್ಗ ಮುದ್ರಿಸು.           // prints 25

    x := ೧೦.
    x > ೫ ? [ "ದೊಡ್ಡ" ] [ "ಚಿಕ್ಕ" ] ಮುದ್ರಿಸು.
"""

__version__ = "0.1.0"
__author__ = "Kapila Project"

from .lexer import tokenize, Lexer, Token, TokenType
from .vm import VM, KapilaError, Block
