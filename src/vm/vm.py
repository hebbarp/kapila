# -*- coding: utf-8 -*-
"""
Kapila Virtual Machine
======================

Perl-style DWIM (Do What I Mean):
- Top level: infix math works (5 * 10)
- Inside blocks: pure postfix Forth-style (dup *)
"""

import os
from typing import Any, Dict, List, Optional
from ..lexer import tokenize, Token, TokenType
from .builtins import BUILTINS
from ..sandarbha import (
    Sandarbha, analyze_vibhakti, VibhaktiResult,
    VERB_FRAMES, NOUN_TYPE_MAP, infer_type,
)

# Word-learning keywords across supported languages
ANDARE_WORDS = frozenset({'ಅಂದರೆ', 'मतलब', 'అంటే'})


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

    def __init__(self, enable_sandarbha=False):
        self.stack: List[Any] = []
        self.words: Dict[str, Block] = {}
        self.variables: Dict[str, Any] = {}
        self.sutras: Dict[str, Block] = {}
        self.builtins = BUILTINS

        # Sandarbha (context resolver) — opt-in
        if enable_sandarbha:
            self.sandarbha = Sandarbha()
            self._stmt_context: List[VibhaktiResult] = []
            self._known_words = self._build_known_words()
        else:
            self.sandarbha = None
            self._stmt_context = []
            self._known_words = frozenset()

        self._load_prelude()

    def _load_prelude(self):
        """Load the standard library prelude if available."""
        lib_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'lib')
        prelude = os.path.join(lib_dir, 'prelude.kpl')
        if os.path.exists(prelude):
            with open(prelude, 'r', encoding='utf-8') as f:
                self.run(f.read())

    def _build_known_words(self) -> frozenset:
        """Build the set of all known words (builtins + vocabulary + keywords).

        This prevents vibhakti decomposition from mangling existing words.
        """
        from ..vocabulary import VOCABULARY
        from ..lexer.keywords import KEYWORDS
        words = set(self.builtins.keys())
        words.update(VOCABULARY.keys())
        words.update(KEYWORDS.keys())
        # Also add ANDARE_WORDS
        words.update(ANDARE_WORDS)
        return frozenset(words)

    def _resolve_stem(self, stem: str):
        """Resolve a vibhakti stem to a value.

        Checks variables, then returns the stem string itself as a symbolic name.
        """
        if stem in self.variables:
            return self.variables[stem]
        return stem

    def _resolve_and_execute(self, verb: str):
        """Resolve missing slots from context, then execute a framed verb.

        Stack-first rule: if the stack already has enough values for all
        slots (from this statement), execute normally — no context needed.

        After execution, record all consumed values in context so future
        bare verbs can reuse them.
        """
        frame = VERB_FRAMES[verb]
        n_slots = len(frame)

        # How many values were pushed onto the stack in this statement?
        n_on_stack = len(self.stack) - getattr(self, '_stmt_stack_start', 0)

        if n_on_stack >= n_slots:
            # Stack-first: all slots filled — peek at values for context, then execute
            # Record the top n_slots values in context (deepest first = frame order)
            slot_values = self.stack[-n_slots:]
            for (role, type_constraint), val in zip(frame, slot_values):
                self.sandarbha.record(val, role, infer_type(str(val), val))
            self._execute_word(verb)
            return

        # Resolve missing slots from context (from first/deepest to last)
        n_provided = n_on_stack
        resolved = []
        for i, (role, type_constraint) in enumerate(frame):
            if i < (n_slots - n_provided):
                # This slot is missing from stack — resolve from context
                value = self.sandarbha.query_role_with_type(role, type_constraint)
                if value is None:
                    raise KapilaError(
                        f"ಸಂದರ್ಭ ದೋಷ: '{verb}' needs '{role}' but no value in context"
                    )
                resolved.append(value)

        # Push resolved values below the already-provided values
        if resolved and n_provided > 0:
            provided_values = []
            for _ in range(n_provided):
                provided_values.append(self.pop())
            provided_values.reverse()
            for val in resolved:
                self.push(val)
            for val in provided_values:
                self.push(val)
        else:
            for val in resolved:
                self.push(val)

        self._execute_word(verb)

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

        # Word learning: name ಅಂದರೆ body ॥
        if (token.type == TokenType.WORD and
            self._peek_type(1) == TokenType.WORD and
            self.pos + 1 < len(self.tokens) and
            self.tokens[self.pos + 1].value in ANDARE_WORDS):
            self._define_word_andare()
            return

        # Assignment: name := expr.
        if token.type == TokenType.WORD and self._peek_type(1) == TokenType.ASSIGN:
            self._assignment()
            return

        # Expression with optional postfix actions
        self._expression_and_actions()

    def _define_word(self):
        """Parse: name: body . (or name: body ॥ for backward compatibility)"""
        name = self._advance().value
        self._advance()  # skip :

        body = []
        # Accept either . (DOT) or ॥ (DEF_END) as terminator
        while self._current().type not in (TokenType.DOT, TokenType.DEF_END, TokenType.EOF):
            body.append(self._advance())

        # Skip the terminator
        if self._current().type in (TokenType.DOT, TokenType.DEF_END):
            self._advance()

        self.words[name] = Block(body)

    def _define_word_andare(self):
        """Parse: name ಅಂದರೆ body . (or ॥)"""
        name = self._advance().value   # word name
        self._advance()                 # skip ಅಂದರೆ/मतलब/అంటే

        body = []
        while self._current().type not in (TokenType.DOT, TokenType.DEF_END, TokenType.EOF):
            body.append(self._advance())

        if self._current().type in (TokenType.DOT, TokenType.DEF_END):
            self._advance()

        self.words[name] = Block(body)

    def _assignment(self):
        """Parse: name := expr."""
        name = self._advance().value
        self._advance()  # skip :=

        value = self._parse_expr()
        self.variables[name] = value

        # Record in sandarbha context for implicit resolution
        if self.sandarbha:
            type_tag = infer_type(name, value)
            self.sandarbha.record(value, 'ವಸ್ತು', type_tag)

        if self._current().type == TokenType.DOT:
            self._advance()

    def _expression_and_actions(self):
        """Parse expression, then postfix actions."""
        # Reset per-statement context for sandarbha
        if self.sandarbha:
            self._stmt_context = []
            self._stmt_stack_start = len(self.stack)

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
                word = self._advance().value
                if self.sandarbha:
                    vr = analyze_vibhakti(word, self._known_words)
                    if vr.role is not None:
                        # Vibhakti-tagged word: resolve stem, push, record
                        resolved = self._resolve_stem(vr.stem)
                        self.push(resolved)
                        self.sandarbha.record(
                            resolved, vr.role, infer_type(vr.stem, resolved)
                        )
                        self._stmt_context.append(vr)
                        continue
                    if word in VERB_FRAMES:
                        # Framed verb: resolve missing slots, then execute
                        self._resolve_and_execute(word)
                        self._stmt_context = []
                        continue
                    # Check for bare noun as type hint
                    if word in NOUN_TYPE_MAP:
                        type_val = self.sandarbha.query_type(NOUN_TYPE_MAP[word])
                        if type_val is not None:
                            self.push(type_val)
                            self._stmt_context.append(
                                VibhaktiResult(stem=word, role=None)
                            )
                            continue
                self._execute_word(word)
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
        """Parse [ ... ] - list if all values, block if has words/ops."""
        self._advance()  # skip [

        # Collect items
        items = []
        has_action = False

        start_pos = self.pos
        depth = 1

        # Token types that indicate this is a block (deferred execution)
        action_types = {
            TokenType.PLUS, TokenType.MINUS, TokenType.STAR,
            TokenType.SLASH, TokenType.PERCENT,
            TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.GT,
            TokenType.LTE, TokenType.GTE,
            TokenType.ARROW, TokenType.PIPE, TokenType.ASSIGN,
        }

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
                # It's a block if it contains builtins, user words, or variables
                if name in self.builtins or name in self.words or name in self.variables:
                    has_action = True
            elif t.type in action_types:
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
        """Parse block contents until ].

        Supports: [ x y -> ... ] or [ x y ಆಗಿ ... ] or [ x y | ... ]
        """
        params = []

        # Check for params with arrow (->) or pipe (|) or Kannada arrow (ಆಗಿ)
        saved = self.pos
        has_params = False

        while self._current().type == TokenType.WORD:
            word = self._current()
            # Check for Kannada arrow ಆಗಿ
            if word.value == 'ಆಗಿ':
                has_params = True
                self._advance()  # skip ಆಗಿ
                break
            # Check for -> or | after collecting param
            params.append(self._advance().value)
            if self._current().type == TokenType.ARROW or self._current().type == TokenType.PIPE:
                has_params = True
                self._advance()  # skip -> or |
                break

        if not has_params:
            self.pos = saved
            params = []

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

        if self.sandarbha:
            self.sandarbha.push_scope()

        # Bind params
        saved_vars = {}
        for param in reversed(block.params):
            saved_vars[param] = self.variables.get(param)
            self.variables[param] = self.pop()

        # Execute in postfix mode, handling assignments and inline blocks
        i = 0
        while i < len(block.tokens):
            token = block.tokens[i]

            # Check for assignment pattern: value name :=
            if (token.type == TokenType.WORD and
                i + 1 < len(block.tokens) and
                block.tokens[i + 1].type == TokenType.ASSIGN):
                name = token.value
                value = self.pop()
                self.variables[name] = value
                i += 2  # skip name and :=
                continue

            # Handle inline blocks: [ ... ] -> push Block onto stack
            if token.type == TokenType.LBRACKET:
                inner_tokens = []
                depth = 1
                i += 1  # skip [
                while i < len(block.tokens) and depth > 0:
                    t = block.tokens[i]
                    if t.type == TokenType.LBRACKET:
                        depth += 1
                    elif t.type == TokenType.RBRACKET:
                        depth -= 1
                        if depth == 0:
                            i += 1  # skip ]
                            break
                    inner_tokens.append(t)
                    i += 1
                self.push(Block(inner_tokens))
                continue

            self._execute_token(token)
            i += 1

        # Restore
        for param, val in saved_vars.items():
            if val is None:
                self.variables.pop(param, None)
            else:
                self.variables[param] = val

        if self.sandarbha:
            self.sandarbha.pop_scope()

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
            elif self.sandarbha:
                vr = analyze_vibhakti(name, self._known_words)
                if vr.role is not None:
                    resolved = self._resolve_stem(vr.stem)
                    self.push(resolved)
                    self.sandarbha.record(
                        resolved, vr.role, infer_type(vr.stem, resolved)
                    )
                elif name in VERB_FRAMES:
                    self._resolve_and_execute(name)
                elif name in self.variables:
                    self.push(self.variables[name])
                elif name in self.builtins:
                    self.builtins[name](self)
                elif name in self.words:
                    self._run_block(self.words[name])
                elif name in NOUN_TYPE_MAP:
                    type_val = self.sandarbha.query_type(NOUN_TYPE_MAP[name])
                    if type_val is not None:
                        self.push(type_val)
                    else:
                        raise KapilaError(f"Unknown word: {name}")
                else:
                    raise KapilaError(f"Unknown word: {name}")
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
