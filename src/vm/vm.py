# -*- coding: utf-8 -*-
"""
Kapila Virtual Machine
======================

Perl-style DWIM (Do What I Mean):
- Top level: infix math works (5 * 10)
- Inside blocks: pure postfix Forth-style (dup *)
"""

from typing import Any, Dict, List, Optional
from ..lexer import tokenize, Token, TokenType
from .builtins import BUILTINS


class KapilaError(Exception):
    """Runtime error in Kapila."""
    pass


class Block:
    """A quoted block of code."""
    def __init__(self, tokens: List[Token], params: List[str] = None):
        self.tokens = tokens
        self.params = params or []

    def __repr__(self):
        return f"Block({len(self.tokens)} tokens)"


class VM:
    """Kapila virtual machine."""

    def __init__(self):
        self.stack: List[Any] = []
        self.words: Dict[str, Block] = {}
        self.variables: Dict[str, Any] = {}
        self.builtins = BUILTINS

    def push(self, value: Any):
        self.stack.append(value)

    def pop(self) -> Any:
        if not self.stack:
            raise KapilaError("Stack underflow")
        return self.stack.pop()

    def peek(self) -> Any:
        if not self.stack:
            raise KapilaError("Stack empty")
        return self.stack[-1]

    def run(self, source: str) -> Any:
        """Run source code (top-level, allows infix)."""
        tokens = tokenize(source)
        return self._run_toplevel(tokens)

    def _run_toplevel(self, tokens: List[Token]):
        """Execute tokens at top level (infix allowed)."""
        self.tokens = tokens
        self.pos = 0

        while not self._at_end():
            self._toplevel_statement()

        return self.stack[-1] if self.stack else None

    def _at_end(self) -> bool:
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF

    def _current(self) -> Token:
        if self._at_end():
            return Token(TokenType.EOF, "", 0, 0)
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        token = self._current()
        self.pos += 1
        return token

    def _peek_type(self, offset=0) -> TokenType:
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return TokenType.EOF
        return self.tokens[pos].type

    def _toplevel_statement(self):
        """Parse one top-level statement."""
        token = self._current()

        # Word definition: name: body ॥
        if token.type == TokenType.WORD and self._peek_type(1) == TokenType.COLON:
            self._define_word()
            return

        # Assignment: name := expr.
        if token.type == TokenType.WORD and self._peek_type(1) == TokenType.ASSIGN:
            self._assignment()
            return

        # Expression with optional postfix actions
        self._expression_and_actions()

    def _define_word(self):
        """Parse: name: body ॥"""
        name = self._advance().value
        self._advance()  # skip :

        body = []
        while self._current().type not in (TokenType.DEF_END, TokenType.EOF):
            body.append(self._advance())

        if self._current().type == TokenType.DEF_END:
            self._advance()

        self.words[name] = Block(body)

    def _assignment(self):
        """Parse: name := expr."""
        name = self._advance().value
        self._advance()  # skip :=

        value = self._parse_expr()
        self.variables[name] = value

        if self._current().type == TokenType.DOT:
            self._advance()

    def _expression_and_actions(self):
        """Parse expression, then postfix actions."""
        # Try to parse an infix expression
        value = self._parse_expr()

        if value is not None:
            self.push(value)

        # Now handle postfix actions (words, numbers, etc.)
        while not self._at_end():
            token = self._current()

            if token.type == TokenType.DOT:
                self._advance()
                break

            if token.type in (TokenType.DEF_END, TokenType.RBRACKET, TokenType.EOF):
                break

            if token.type == TokenType.NUMBER:
                # Push number onto stack (Forth-style)
                self.push(self._advance().literal)
            elif token.type == TokenType.STRING:
                # Push string onto stack
                self.push(self._advance().literal)
            elif token.type == TokenType.WORD:
                self._execute_word(self._advance().value)
            elif token.type == TokenType.QUOTE:
                self._advance()
                if self._current().type == TokenType.WORD:
                    self.push(self._advance().value)
            elif token.type == TokenType.LBRACKET:
                self.push(self._parse_block())
            elif token.type == TokenType.LBRACE:
                self.push(self._parse_map())
            elif token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.STAR,
                               TokenType.SLASH, TokenType.PERCENT):
                # Handle operators in postfix position
                self._execute_token(self._advance())
            else:
                break

    # === Infix Expression Parser ===

    def _parse_expr(self) -> Any:
        """Parse infix expression."""
        return self._parse_ternary()

    def _parse_ternary(self) -> Any:
        """expr ? [true] [false]"""
        expr = self._parse_or()

        if self._current().type == TokenType.QUESTION:
            self._advance()
            true_block = self._parse_block()
            false_block = None
            if self._current().type == TokenType.LBRACKET:
                false_block = self._parse_block()

            if expr:
                self._run_block(true_block)
            elif false_block:
                self._run_block(false_block)
            return None  # result is on stack or side effect

        return expr

    def _parse_or(self) -> Any:
        left = self._parse_and()
        while self._current().value in ('ಅಥವಾ', 'or'):
            self._advance()
            left = left or self._parse_and()
        return left

    def _parse_and(self) -> Any:
        left = self._parse_comparison()
        while self._current().value in ('ಮತ್ತು', 'and'):
            self._advance()
            left = left and self._parse_comparison()
        return left

    def _parse_comparison(self) -> Any:
        left = self._parse_additive()

        ops = {
            TokenType.EQ: lambda a, b: a == b,
            TokenType.NEQ: lambda a, b: a != b,
            TokenType.LT: lambda a, b: a < b,
            TokenType.GT: lambda a, b: a > b,
            TokenType.LTE: lambda a, b: a <= b,
            TokenType.GTE: lambda a, b: a >= b,
        }

        while self._current().type in ops:
            op = ops[self._advance().type]
            left = op(left, self._parse_additive())

        return left

    def _parse_additive(self) -> Any:
        left = self._parse_multiplicative()

        while self._current().type in (TokenType.PLUS, TokenType.MINUS):
            if self._advance().type == TokenType.PLUS:
                left = left + self._parse_multiplicative()
            else:
                left = left - self._parse_multiplicative()

        return left

    def _parse_multiplicative(self) -> Any:
        left = self._parse_unary()

        while self._current().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._advance().type
            right = self._parse_unary()
            if op == TokenType.STAR:
                left = left * right
            elif op == TokenType.SLASH:
                left = left / right
            else:
                left = left % right

        return left

    def _parse_unary(self) -> Any:
        if self._current().type == TokenType.MINUS:
            self._advance()
            return -self._parse_unary()
        if self._current().value in ('ಅಲ್ಲ', 'not'):
            self._advance()
            return not self._parse_unary()
        return self._parse_primary()

    def _parse_primary(self) -> Any:
        token = self._current()

        if token.type == TokenType.NUMBER:
            return self._advance().literal

        if token.type == TokenType.STRING:
            return self._advance().literal

        if token.type == TokenType.WORD:
            name = token.value
            if name in self.variables:
                self._advance()
                return self.variables[name]
            if name in ('ನಿಜ', 'true'):
                self._advance()
                return True
            if name in ('ಸುಳ್ಳು', 'false'):
                self._advance()
                return False
            # Not a value, don't consume
            return None

        if token.type == TokenType.LBRACKET:
            return self._parse_list_or_block()

        if token.type == TokenType.LBRACE:
            return self._parse_map()

        return None

    def _parse_list_or_block(self) -> Any:
        """Parse [ ... ] - list if all values, block if has words."""
        self._advance()  # skip [

        # Collect items
        items = []
        has_action = False

        start_pos = self.pos
        depth = 1

        # Scan to see what's inside
        while depth > 0 and not self._at_end():
            t = self._current()
            if t.type == TokenType.LBRACKET:
                depth += 1
            elif t.type == TokenType.RBRACKET:
                depth -= 1
                if depth == 0:
                    break
            elif t.type == TokenType.WORD:
                name = t.value
                if name in self.builtins or name in self.words:
                    has_action = True
            self._advance()

        # Reset
        self.pos = start_pos

        if has_action:
            return self._parse_block_body()
        else:
            # Parse as list
            items = []
            while self._current().type != TokenType.RBRACKET:
                if self._at_end():
                    raise KapilaError("Unterminated list")
                val = self._parse_expr()
                if val is not None:
                    items.append(val)
                else:
                    self._advance()  # skip unknown
            self._advance()  # skip ]
            return items

    def _parse_block(self) -> Block:
        """Parse [ ... ] as block."""
        if self._current().type != TokenType.LBRACKET:
            raise KapilaError("Expected '['")
        self._advance()
        return self._parse_block_body()

    def _parse_block_body(self) -> Block:
        """Parse block contents until ]."""
        params = []

        # Check for params: [ x y | ... ]
        saved = self.pos
        while self._current().type == TokenType.WORD:
            if self._peek_type(1) == TokenType.PIPE:
                # Has params
                while self._current().type == TokenType.WORD:
                    params.append(self._advance().value)
                    if self._current().type == TokenType.PIPE:
                        self._advance()
                        break
                break
            else:
                break

        if not params:
            self.pos = saved

        # Collect body tokens
        tokens = []
        depth = 1
        while depth > 0:
            if self._at_end():
                raise KapilaError("Unterminated block")
            t = self._current()
            if t.type == TokenType.LBRACKET:
                depth += 1
            elif t.type == TokenType.RBRACKET:
                depth -= 1
                if depth == 0:
                    break
            tokens.append(self._advance())

        self._advance()  # skip ]
        return Block(tokens, params)

    def _parse_map(self) -> Dict:
        """Parse { key: value ... }"""
        self._advance()  # skip {
        data = {}

        while self._current().type != TokenType.RBRACE:
            if self._at_end():
                raise KapilaError("Unterminated map")

            if self._current().type == TokenType.WORD:
                key = self._advance().value
                if self._current().type == TokenType.COLON:
                    self._advance()
                    data[key] = self._parse_expr()
            else:
                self._advance()

        self._advance()  # skip }
        return data

    # === Word Execution ===

    def _execute_word(self, name: str):
        """Execute a word."""
        if name in self.builtins:
            self.builtins[name](self)
        elif name in self.words:
            self._run_block(self.words[name])
        elif name in self.variables:
            self.push(self.variables[name])
        else:
            raise KapilaError(f"Unknown word: {name}")

    def _run_block(self, block: Block):
        """Execute a block (pure postfix Forth-style)."""
        if isinstance(block, str):
            self._execute_word(block)
            return

        # Bind params
        saved_vars = {}
        for param in reversed(block.params):
            saved_vars[param] = self.variables.get(param)
            self.variables[param] = self.pop()

        # Execute in postfix mode
        for token in block.tokens:
            self._execute_token(token)

        # Restore
        for param, val in saved_vars.items():
            if val is None:
                self.variables.pop(param, None)
            else:
                self.variables[param] = val

    def _execute_token(self, token: Token):
        """Execute single token in postfix mode."""
        if token.type == TokenType.NUMBER:
            self.push(token.literal)

        elif token.type == TokenType.STRING:
            self.push(token.literal)

        elif token.type == TokenType.WORD:
            name = token.value
            if name in ('ನಿಜ', 'true'):
                self.push(True)
            elif name in ('ಸುಳ್ಳು', 'false'):
                self.push(False)
            elif name in self.variables:
                self.push(self.variables[name])
            elif name in self.builtins:
                self.builtins[name](self)
            elif name in self.words:
                self._run_block(self.words[name])
            else:
                raise KapilaError(f"Unknown word: {name}")

        elif token.type == TokenType.PLUS:
            b, a = self.pop(), self.pop()
            self.push(a + b)

        elif token.type == TokenType.MINUS:
            b, a = self.pop(), self.pop()
            self.push(a - b)

        elif token.type == TokenType.STAR:
            b, a = self.pop(), self.pop()
            self.push(a * b)

        elif token.type == TokenType.SLASH:
            b, a = self.pop(), self.pop()
            self.push(a / b)

        elif token.type == TokenType.PERCENT:
            b, a = self.pop(), self.pop()
            self.push(a % b)

        elif token.type == TokenType.EQ:
            b, a = self.pop(), self.pop()
            self.push(a == b)

        elif token.type == TokenType.LT:
            b, a = self.pop(), self.pop()
            self.push(a < b)

        elif token.type == TokenType.GT:
            b, a = self.pop(), self.pop()
            self.push(a > b)

        elif token.type == TokenType.LTE:
            b, a = self.pop(), self.pop()
            self.push(a <= b)

        elif token.type == TokenType.GTE:
            b, a = self.pop(), self.pop()
            self.push(a >= b)

        elif token.type == TokenType.NEQ:
            b, a = self.pop(), self.pop()
            self.push(a != b)

    def execute_quotation(self, block):
        """Public method for builtins to execute blocks."""
        self._run_block(block)
