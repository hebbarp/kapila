# -*- coding: utf-8 -*-
"""
Kapila Lexer
============

Tokenizes Kapila source code into a stream of tokens.

Handles:
- Kannada and ASCII identifiers
- Kannada (೦-೯) and ASCII (0-9) numbers
- Strings with escape sequences
- Operators and delimiters
- Comments (// single line, /* multi-line */)
"""

from typing import Iterator, List, Optional
from .tokens import Token, TokenType
from ..unicode import (
    is_kannada_char,
    is_valid_identifier_start,
    is_valid_identifier_char,
    is_kannada_digit,
    kannada_digit_value,
)


class Lexer:
    """Kapila lexer/scanner."""

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.start = 0
        self.start_line = 1
        self.start_column = 1

    def __iter__(self) -> Iterator[Token]:
        return self

    def __next__(self) -> Token:
        token = self.next_token()
        if token.type == TokenType.EOF:
            raise StopIteration
        return token

    def scan_all(self) -> List[Token]:
        """Scan all tokens."""
        tokens = []
        while True:
            token = self.next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens

    def next_token(self) -> Token:
        """Get next token."""
        self._skip_whitespace_and_comments()

        if self._at_end():
            return self._make_token(TokenType.EOF, "")

        self._mark_start()
        ch = self._advance()

        # Numbers
        if ch.isdigit() or is_kannada_digit(ch):
            return self._scan_number(ch)

        # Strings
        if ch == '"':
            return self._scan_string()

        # Words/identifiers
        if self._is_word_start(ch):
            return self._scan_word(ch)

        # Two-character tokens (check first)
        if ch == ':' and self._peek() == '=':
            self._advance()
            return self._make_token(TokenType.ASSIGN, ":=")
        if ch == '!' and self._peek() == '=':
            self._advance()
            return self._make_token(TokenType.NEQ, "!=")
        if ch == '<' and self._peek() == '=':
            self._advance()
            return self._make_token(TokenType.LTE, "<=")
        if ch == '>' and self._peek() == '=':
            self._advance()
            return self._make_token(TokenType.GTE, ">=")

        # Single-character tokens
        simple_tokens = {
            '.': TokenType.DOT,
            ':': TokenType.COLON,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '|': TokenType.PIPE,
            "'": TokenType.QUOTE,
            '?': TokenType.QUESTION,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '%': TokenType.PERCENT,
            '=': TokenType.EQ,
            '<': TokenType.LT,
            '>': TokenType.GT,
            '≠': TokenType.NEQ,
            '≤': TokenType.LTE,
            '≥': TokenType.GTE,
        }

        if ch in simple_tokens:
            return self._make_token(simple_tokens[ch], ch)

        # Double danda (definition end)
        if ch == '॥':
            return self._make_token(TokenType.DEF_END, ch)

        # Unknown
        return self._error_token(f"Unexpected character: {ch!r}")

    # === Character handling ===

    def _at_end(self) -> bool:
        return self.pos >= len(self.source)

    def _peek(self) -> str:
        if self._at_end():
            return '\0'
        return self.source[self.pos]

    def _peek_next(self) -> str:
        if self.pos + 1 >= len(self.source):
            return '\0'
        return self.source[self.pos + 1]

    def _advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _mark_start(self):
        self.start = self.pos
        self.start_line = self.line
        self.start_column = self.column

    # === Whitespace and comments ===

    def _skip_whitespace_and_comments(self):
        while not self._at_end():
            ch = self._peek()

            if ch in ' \t\r\n':
                self._advance()
            elif ch == '/' and self._peek_next() == '/':
                self._skip_line_comment()
            elif ch == '/' and self._peek_next() == '*':
                self._skip_block_comment()
            else:
                break

    def _skip_line_comment(self):
        self._advance()  # /
        self._advance()  # /
        while not self._at_end() and self._peek() != '\n':
            self._advance()

    def _skip_block_comment(self):
        self._advance()  # /
        self._advance()  # *
        while not self._at_end():
            if self._peek() == '*' and self._peek_next() == '/':
                self._advance()
                self._advance()
                return
            self._advance()

    # === Token scanners ===

    def _is_word_start(self, ch: str) -> bool:
        """Check if character can start a word."""
        if ch == '_':
            return True
        if ch.isalpha():
            return True
        if is_valid_identifier_start(ch):
            return True
        return False

    def _is_word_char(self, ch: str) -> bool:
        """Check if character can continue a word."""
        if ch == '_' or ch == '-':  # allow kebab-case
            return True
        if ch.isalnum():
            return True
        if is_valid_identifier_char(ch):
            return True
        return False

    def _scan_word(self, first_char: str) -> Token:
        """Scan a word/identifier."""
        chars = [first_char]
        while not self._at_end() and self._is_word_char(self._peek()):
            chars.append(self._advance())
        text = ''.join(chars)
        return self._make_token(TokenType.WORD, text)

    def _scan_number(self, first_char: str) -> Token:
        """Scan a number (integer or float)."""
        chars = [first_char]
        has_dot = False

        while not self._at_end():
            ch = self._peek()
            if ch.isdigit() or is_kannada_digit(ch):
                chars.append(self._advance())
            elif ch == '.' and not has_dot:
                # Look ahead - is this a decimal point or statement end?
                next_ch = self._peek_next()
                if next_ch.isdigit() or is_kannada_digit(next_ch):
                    has_dot = True
                    chars.append(self._advance())
                else:
                    break
            else:
                break

        text = ''.join(chars)
        value = self._parse_number(text, has_dot)
        return self._make_token(TokenType.NUMBER, text, value)

    def _parse_number(self, text: str, is_float: bool) -> float | int:
        """Convert number string (possibly with Kannada digits) to value."""
        normalized = []
        for ch in text:
            kv = kannada_digit_value(ch)
            if kv is not None:
                normalized.append(str(kv))
            else:
                normalized.append(ch)
        num_str = ''.join(normalized)
        return float(num_str) if is_float else int(num_str)

    def _scan_string(self) -> Token:
        """Scan a string literal."""
        chars = []
        start_line = self.line

        while not self._at_end() and self._peek() != '"':
            ch = self._peek()
            if ch == '\\':
                self._advance()
                if self._at_end():
                    return self._error_token("Unterminated string")
                escape = self._advance()
                escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', '0': '\0'}
                chars.append(escape_map.get(escape, escape))
            else:
                chars.append(self._advance())

        if self._at_end():
            return self._error_token(f"Unterminated string (started line {start_line})")

        self._advance()  # closing "
        text = self.source[self.start:self.pos]
        literal = ''.join(chars)
        return self._make_token(TokenType.STRING, text, literal)

    # === Token creation ===

    def _make_token(self, type: TokenType, value: str, literal=None) -> Token:
        return Token(type, value, self.start_line, self.start_column, literal)

    def _error_token(self, message: str) -> Token:
        return Token(TokenType.ERROR, message, self.start_line, self.start_column)


def tokenize(source: str) -> List[Token]:
    """Tokenize source code."""
    return Lexer(source).scan_all()
