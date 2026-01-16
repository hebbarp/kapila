# -*- coding: utf-8 -*-
"""
Kapila Parser
=============

Recursive descent parser that converts tokens to AST.

Grammar (informal):
    program     → statement* EOF
    statement   → wordDef | varAssign | exprStmt
    wordDef     → WORD ':' token* '॥'
    varAssign   → WORD ':=' expr '.'
    exprStmt    → expr actions? '.'?

    expr        → ternary
    ternary     → or ('?' block block?)?
    or          → and (('ಅಥವಾ'|'or') and)*
    and         → comparison (('ಮತ್ತು'|'and') comparison)*
    comparison  → additive (('='|'!='|'<'|'>'|'<='|'>=') additive)*
    additive    → multiplicative (('+'|'-') multiplicative)*
    multiplicative → unary (('*'|'/'|'%') unary)*
    unary       → ('-'|'ಅಲ್ಲ'|'not')? primary
    primary     → NUMBER | STRING | WORD | block | list | map | '(' expr ')'

    block       → '[' params? body ']'
    list        → '[' expr* ']'  (when all are values)
    map         → '{' (WORD ':' expr)* '}'
    actions     → WORD+
"""

from typing import List, Optional, Union
from ..lexer import Token, TokenType, tokenize
from .ast import (
    Node, Expr, Stmt, Program,
    NumberLit, StringLit, BoolLit, Word, QuotedWord,
    Block, ListLit, MapLit,
    BinaryExpr, UnaryExpr, Conditional, PostfixAction,
    WordDef, VarAssign, ExprStmt,
)


class ParseError(Exception):
    """Error during parsing."""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Line {line}:{column}: {message}")


class Parser:
    """Recursive descent parser for Kapila."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors: List[ParseError] = []

    def parse(self) -> Program:
        """Parse tokens into a Program AST."""
        statements = []

        while not self._at_end():
            try:
                stmt = self._statement()
                if stmt:
                    statements.append(stmt)
            except ParseError as e:
                self.errors.append(e)
                self._synchronize()

        return Program(statements=statements)

    # === Helper Methods ===

    def _at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        if self.pos >= len(self.tokens):
            return Token(TokenType.EOF, "", 0, 0)
        return self.tokens[self.pos]

    def _peek_next(self) -> Token:
        if self.pos + 1 >= len(self.tokens):
            return Token(TokenType.EOF, "", 0, 0)
        return self.tokens[self.pos + 1]

    def _advance(self) -> Token:
        token = self._peek()
        if not self._at_end():
            self.pos += 1
        return token

    def _check(self, type: TokenType) -> bool:
        return self._peek().type == type

    def _match(self, *types: TokenType) -> Optional[Token]:
        for t in types:
            if self._check(t):
                return self._advance()
        return None

    def _expect(self, type: TokenType, message: str) -> Token:
        if self._check(type):
            return self._advance()
        token = self._peek()
        raise ParseError(message, token.line, token.column)

    def _synchronize(self):
        """Skip tokens until we find a statement boundary."""
        self._advance()
        while not self._at_end():
            if self._peek().type in (TokenType.DOT, TokenType.DEF_END):
                self._advance()
                return
            if self._peek().type == TokenType.WORD and self._peek_next().type == TokenType.COLON:
                return
            self._advance()

    # === Statement Parsing ===

    def _statement(self) -> Optional[Stmt]:
        """Parse a statement."""
        token = self._peek()

        # Word definition: name: body ॥
        if token.type == TokenType.WORD and self._peek_next().type == TokenType.COLON:
            return self._word_def()

        # Variable assignment: name := expr.
        if token.type == TokenType.WORD and self._peek_next().type == TokenType.ASSIGN:
            return self._var_assign()

        # Expression statement
        return self._expr_stmt()

    def _word_def(self) -> WordDef:
        """Parse: name: body ॥"""
        name_token = self._advance()
        name = name_token.value
        self._advance()  # skip :

        body = []
        while not self._check(TokenType.DEF_END) and not self._at_end():
            # Inside word definitions, we collect raw expressions
            # This is Forth-style: the body is postfix
            elem = self._parse_body_element()
            if elem:
                body.append(elem)

        self._match(TokenType.DEF_END)

        return WordDef(
            name=name,
            body=body,
            line=name_token.line,
            column=name_token.column
        )

    def _parse_body_element(self) -> Optional[Union[Expr, Stmt]]:
        """Parse a single element inside a word definition body."""
        token = self._peek()

        if token.type == TokenType.NUMBER:
            return self._number()

        if token.type == TokenType.STRING:
            return self._string()

        if token.type == TokenType.WORD:
            return self._word()

        if token.type == TokenType.LBRACKET:
            return self._block()

        if token.type == TokenType.LBRACE:
            return self._map()

        if token.type == TokenType.QUOTE:
            return self._quoted_word()

        if token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.STAR,
                          TokenType.SLASH, TokenType.PERCENT,
                          TokenType.EQ, TokenType.NEQ, TokenType.LT,
                          TokenType.GT, TokenType.LTE, TokenType.GTE):
            # Operator as word (postfix)
            op_token = self._advance()
            return Word(name=op_token.value, line=op_token.line, column=op_token.column)

        # Skip unknown tokens
        self._advance()
        return None

    def _var_assign(self) -> VarAssign:
        """Parse: name := expr."""
        name_token = self._advance()
        name = name_token.value
        self._advance()  # skip :=

        value = self._expression()

        self._match(TokenType.DOT)

        return VarAssign(
            name=name,
            value=value,
            line=name_token.line,
            column=name_token.column
        )

    def _expr_stmt(self) -> ExprStmt:
        """Parse expression followed by optional postfix actions."""
        start_token = self._peek()
        expr = self._expression()

        # Check for postfix actions (words after the expression)
        actions = []
        while self._check(TokenType.WORD) and not self._at_end():
            word_token = self._advance()
            # Stop if this word starts a new definition
            if self._check(TokenType.COLON) or self._check(TokenType.ASSIGN):
                self.pos -= 1  # put the word back
                break
            actions.append(Word(
                name=word_token.value,
                line=word_token.line,
                column=word_token.column
            ))

        # If we have actions, wrap in PostfixAction
        if actions:
            expr = PostfixAction(
                value=expr,
                actions=actions,
                line=start_token.line,
                column=start_token.column
            )

        self._match(TokenType.DOT)

        return ExprStmt(
            expr=expr,
            line=start_token.line,
            column=start_token.column
        )

    # === Expression Parsing ===

    def _expression(self) -> Expr:
        """Parse an expression."""
        return self._ternary()

    def _ternary(self) -> Expr:
        """Parse: expr ? [true] [false]"""
        expr = self._or()

        if self._match(TokenType.QUESTION):
            true_block = self._block()
            false_block = None
            if self._check(TokenType.LBRACKET):
                false_block = self._block()

            return Conditional(
                condition=expr,
                true_block=true_block,
                false_block=false_block,
                line=expr.line,
                column=expr.column
            )

        return expr

    def _or(self) -> Expr:
        """Parse: and (('ಅಥವಾ'|'or') and)*"""
        left = self._and()

        while self._check(TokenType.WORD) and self._peek().value in ('ಅಥವಾ', 'or'):
            op_token = self._advance()
            right = self._and()
            left = BinaryExpr(
                left=left,
                op=op_token.value,
                right=right,
                line=left.line,
                column=left.column
            )

        return left

    def _and(self) -> Expr:
        """Parse: comparison (('ಮತ್ತು'|'and') comparison)*"""
        left = self._comparison()

        while self._check(TokenType.WORD) and self._peek().value in ('ಮತ್ತು', 'and'):
            op_token = self._advance()
            right = self._comparison()
            left = BinaryExpr(
                left=left,
                op=op_token.value,
                right=right,
                line=left.line,
                column=left.column
            )

        return left

    def _comparison(self) -> Expr:
        """Parse: additive (('='|'!='|'<'|'>'|'<='|'>=') additive)*"""
        left = self._additive()

        op_types = {
            TokenType.EQ: '=',
            TokenType.NEQ: '!=',
            TokenType.LT: '<',
            TokenType.GT: '>',
            TokenType.LTE: '<=',
            TokenType.GTE: '>=',
        }

        while self._peek().type in op_types:
            op_token = self._advance()
            right = self._additive()
            left = BinaryExpr(
                left=left,
                op=op_types[op_token.type],
                right=right,
                line=left.line,
                column=left.column
            )

        return left

    def _additive(self) -> Expr:
        """Parse: multiplicative (('+'|'-') multiplicative)*"""
        left = self._multiplicative()

        while self._peek().type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self._advance()
            right = self._multiplicative()
            left = BinaryExpr(
                left=left,
                op=op_token.value,
                right=right,
                line=left.line,
                column=left.column
            )

        return left

    def _multiplicative(self) -> Expr:
        """Parse: unary (('*'|'/'|'%') unary)*"""
        left = self._unary()

        while self._peek().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_token = self._advance()
            right = self._unary()
            left = BinaryExpr(
                left=left,
                op=op_token.value,
                right=right,
                line=left.line,
                column=left.column
            )

        return left

    def _unary(self) -> Expr:
        """Parse: ('-'|'ಅಲ್ಲ'|'not')? primary"""
        if self._match(TokenType.MINUS):
            operand = self._unary()
            return UnaryExpr(
                op='-',
                operand=operand,
                line=operand.line,
                column=operand.column
            )

        if self._check(TokenType.WORD) and self._peek().value in ('ಅಲ್ಲ', 'not'):
            op_token = self._advance()
            operand = self._unary()
            return UnaryExpr(
                op=op_token.value,
                operand=operand,
                line=op_token.line,
                column=op_token.column
            )

        return self._primary()

    def _primary(self) -> Expr:
        """Parse: NUMBER | STRING | WORD | block | list | map"""
        token = self._peek()

        if token.type == TokenType.NUMBER:
            return self._number()

        if token.type == TokenType.STRING:
            return self._string()

        if token.type == TokenType.WORD:
            return self._word_or_bool()

        if token.type == TokenType.LBRACKET:
            return self._block_or_list()

        if token.type == TokenType.LBRACE:
            return self._map()

        if token.type == TokenType.QUOTE:
            return self._quoted_word()

        # If nothing matches, return an empty Word (will be handled as error later)
        return Word(name="", line=token.line, column=token.column)

    def _number(self) -> NumberLit:
        """Parse a number literal."""
        token = self._advance()
        return NumberLit(
            value=token.literal,
            line=token.line,
            column=token.column
        )

    def _string(self) -> StringLit:
        """Parse a string literal."""
        token = self._advance()
        return StringLit(
            value=token.literal,
            line=token.line,
            column=token.column
        )

    def _word(self) -> Word:
        """Parse a word."""
        token = self._advance()
        return Word(
            name=token.value,
            line=token.line,
            column=token.column
        )

    def _word_or_bool(self) -> Expr:
        """Parse a word, checking for boolean literals."""
        token = self._peek()

        if token.value in ('ನಿಜ', 'true'):
            self._advance()
            return BoolLit(value=True, line=token.line, column=token.column)

        if token.value in ('ಸುಳ್ಳು', 'false'):
            self._advance()
            return BoolLit(value=False, line=token.line, column=token.column)

        return self._word()

    def _quoted_word(self) -> QuotedWord:
        """Parse: 'word"""
        self._advance()  # skip '
        if self._check(TokenType.WORD):
            token = self._advance()
            return QuotedWord(
                name=token.value,
                line=token.line,
                column=token.column
            )
        token = self._peek()
        raise ParseError("Expected word after quote", token.line, token.column)

    def _block_or_list(self) -> Union[Block, ListLit]:
        """
        Parse [ ... ] - determine if it's a block or list.

        List if all elements are literals.
        Block if it contains words/operations.
        """
        start_token = self._peek()
        self._advance()  # skip [

        # Scan ahead to determine type
        saved_pos = self.pos
        is_block = False

        depth = 1
        while depth > 0 and not self._at_end():
            token = self._peek()
            if token.type == TokenType.LBRACKET:
                depth += 1
            elif token.type == TokenType.RBRACKET:
                depth -= 1
                if depth == 0:
                    break
            elif token.type == TokenType.WORD:
                # Check if it's a boolean or an action word
                if token.value not in ('ನಿಜ', 'true', 'ಸುಳ್ಳು', 'false'):
                    is_block = True
            elif token.type == TokenType.PIPE:
                is_block = True
            elif token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.STAR,
                               TokenType.SLASH, TokenType.PERCENT,
                               TokenType.EQ, TokenType.NEQ, TokenType.LT,
                               TokenType.GT, TokenType.LTE, TokenType.GTE):
                is_block = True
            self._advance()

        # Reset position
        self.pos = saved_pos

        if is_block:
            return self._block_body(start_token)
        else:
            return self._list_body(start_token)

    def _block(self) -> Block:
        """Parse a block unconditionally."""
        start_token = self._peek()
        self._expect(TokenType.LBRACKET, "Expected '['")
        return self._block_body(start_token)

    def _block_body(self, start_token: Token) -> Block:
        """Parse block contents: [ params | body ]"""
        params = []

        # Check for params: x y |
        saved_pos = self.pos
        has_params = False

        # Look for pipe
        temp_params = []
        while self._check(TokenType.WORD):
            temp_params.append(self._advance().value)
            if self._check(TokenType.PIPE):
                has_params = True
                self._advance()  # skip |
                params = temp_params
                break

        if not has_params:
            self.pos = saved_pos

        # Parse body
        body = []
        while not self._check(TokenType.RBRACKET) and not self._at_end():
            elem = self._parse_body_element()
            if elem:
                body.append(elem)

        self._expect(TokenType.RBRACKET, "Expected ']'")

        return Block(
            params=params,
            body=body,
            line=start_token.line,
            column=start_token.column
        )

    def _list_body(self, start_token: Token) -> ListLit:
        """Parse list contents: [ elem elem ... ]"""
        elements = []

        while not self._check(TokenType.RBRACKET) and not self._at_end():
            elem = self._expression()
            if elem:
                elements.append(elem)

        self._expect(TokenType.RBRACKET, "Expected ']'")

        return ListLit(
            elements=elements,
            line=start_token.line,
            column=start_token.column
        )

    def _map(self) -> MapLit:
        """Parse: { key: value ... }"""
        start_token = self._advance()  # skip {
        pairs = []

        while not self._check(TokenType.RBRACE) and not self._at_end():
            if self._check(TokenType.WORD):
                key = self._advance().value
                if self._match(TokenType.COLON):
                    value = self._expression()
                    pairs.append((key, value))
            else:
                self._advance()  # skip unknown

        self._expect(TokenType.RBRACE, "Expected '}'")

        return MapLit(
            pairs=pairs,
            line=start_token.line,
            column=start_token.column
        )


def parse(source: str) -> Program:
    """Parse source code into an AST."""
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()
