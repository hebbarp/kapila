# -*- coding: utf-8 -*-
"""
Kapila Type Checker
===================

Walks the AST and performs type checking/inference.
"""

from typing import List, Optional
from dataclasses import dataclass

from ..parser.ast import (
    Node, Expr, Stmt, Program,
    NumberLit, StringLit, BoolLit, Word, QuotedWord,
    Block, ListLit, MapLit,
    BinaryExpr, UnaryExpr, Conditional, PostfixAction,
    WordDef, VarAssign, ExprStmt,
    NodeVisitor
)

from .types import (
    Type, INT, FLOAT, NUMBER, STRING, BOOL, VOID, ANY,
    IntType, FloatType, NumberType, StringType, BoolType,
    ListType, MapType, BlockType, AnyType,
    SymbolTable, Symbol, create_builtin_symbols,
    type_from_value, common_type
)


@dataclass
class TypeError:
    """A type error."""
    message: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"ದೋಷ (line {self.line}): {self.message}"

    def kannada_message(self) -> str:
        """Return error message in Kannada."""
        return f"ಮಾದರಿ ದೋಷ (ಸಾಲು {self.line}): {self.message}"


class TypeChecker(NodeVisitor):
    """
    Type checker for Kapila.

    Walks the AST and:
    1. Infers types for expressions
    2. Checks type compatibility
    3. Reports type errors
    """

    def __init__(self):
        self.symbols = create_builtin_symbols()
        self.errors: List[TypeError] = []
        # Stack type simulation for Forth-style checking
        self.type_stack: List[Type] = []

    def check(self, program: Program) -> List[TypeError]:
        """Type check a program."""
        self.visit(program)
        return self.errors

    def error(self, message: str, node: Node):
        """Record a type error."""
        self.errors.append(TypeError(message, node.line, node.column))

    # === Visitor Methods ===

    def visit_Program(self, node: Program) -> Type:
        for stmt in node.statements:
            self.visit(stmt)
        return VOID

    def visit_ExprStmt(self, node: ExprStmt) -> Type:
        return self.visit(node.expr)

    def visit_VarAssign(self, node: VarAssign) -> Type:
        value_type = self.visit(node.value)
        self.symbols.define(node.name, value_type)
        return VOID

    def visit_WordDef(self, node: WordDef) -> Type:
        # Create a block type for the word
        # For now, use Any since we don't analyze the body deeply
        word_type = BlockType(return_type=ANY)
        self.symbols.define(node.name, word_type)
        return VOID

    def visit_NumberLit(self, node: NumberLit) -> Type:
        if isinstance(node.value, int):
            return INT
        return FLOAT

    def visit_StringLit(self, node: StringLit) -> Type:
        return STRING

    def visit_BoolLit(self, node: BoolLit) -> Type:
        return BOOL

    def visit_Word(self, node: Word) -> Type:
        symbol = self.symbols.lookup(node.name)
        if symbol:
            return symbol.type
        # Unknown word - might be defined later
        return ANY

    def visit_QuotedWord(self, node: QuotedWord) -> Type:
        # Quoted word is a symbol (string-like)
        return STRING

    def visit_ListLit(self, node: ListLit) -> Type:
        if not node.elements:
            return ListType(ANY)

        # Infer element type from elements
        elem_types = [self.visit(e) for e in node.elements]
        elem_type = elem_types[0]
        for t in elem_types[1:]:
            elem_type = common_type(elem_type, t)

        return ListType(elem_type)

    def visit_MapLit(self, node: MapLit) -> Type:
        if not node.pairs:
            return MapType(STRING, ANY)

        # Infer value type
        value_types = [self.visit(v) for _, v in node.pairs]
        value_type = value_types[0] if value_types else ANY
        for t in value_types[1:]:
            value_type = common_type(value_type, t)

        return MapType(STRING, value_type)

    def visit_Block(self, node: Block) -> Type:
        # Create child scope for block
        old_symbols = self.symbols
        self.symbols = self.symbols.create_child()

        # Define parameters
        param_types = []
        for param in node.params:
            self.symbols.define(param, ANY)
            param_types.append(ANY)

        # Type check body (simplified)
        return_type = VOID
        for item in node.body:
            return_type = self.visit(item)

        self.symbols = old_symbols

        return BlockType(
            param_types=param_types,
            return_type=return_type,
            consumes=len(node.params),
            produces=1 if return_type != VOID else 0
        )

    def visit_BinaryExpr(self, node: BinaryExpr) -> Type:
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        # Arithmetic operators
        if node.op in ['+', '-', '*', '/', '%']:
            if not left_type.is_numeric():
                self.error(f"ಎಡ ಭಾಗ ಸಂಖ್ಯೆ ಆಗಿರಬೇಕು, '{left_type}' ಅಲ್ಲ", node)
            if not right_type.is_numeric():
                self.error(f"ಬಲ ಭಾಗ ಸಂಖ್ಯೆ ಆಗಿರಬೇಕು, '{right_type}' ಅಲ್ಲ", node)

            # Float if either is float
            if isinstance(left_type, FloatType) or isinstance(right_type, FloatType):
                return FLOAT
            if node.op == '/':
                return FLOAT  # Division always returns float
            return NUMBER

        # Comparison operators
        if node.op in ['<', '>', '<=', '>=', '=', '!=']:
            return BOOL

        # Logical operators
        if node.op in ['ಮತ್ತು', 'and', 'ಅಥವಾ', 'or']:
            if not isinstance(left_type, BoolType) and not isinstance(left_type, AnyType):
                self.error(f"ತಾರ್ಕಿಕ ಕಾರ್ಯಕ್ಕೆ ಬೂಲ್ ಬೇಕು, '{left_type}' ಅಲ್ಲ", node)
            return BOOL

        return ANY

    def visit_UnaryExpr(self, node: UnaryExpr) -> Type:
        operand_type = self.visit(node.operand)

        if node.op == '-':
            if not operand_type.is_numeric():
                self.error(f"ಋಣಾತ್ಮಕಕ್ಕೆ ಸಂಖ್ಯೆ ಬೇಕು, '{operand_type}' ಅಲ್ಲ", node)
            return operand_type

        if node.op in ['ಅಲ್ಲ', 'not']:
            if not isinstance(operand_type, BoolType) and not isinstance(operand_type, AnyType):
                self.error(f"'ಅಲ್ಲ' ಕಾರ್ಯಕ್ಕೆ ಬೂಲ್ ಬೇಕು, '{operand_type}' ಅಲ್ಲ", node)
            return BOOL

        return ANY

    def visit_Conditional(self, node: Conditional) -> Type:
        cond_type = self.visit(node.condition)

        if not isinstance(cond_type, BoolType) and not isinstance(cond_type, AnyType):
            self.error(f"ಷರತ್ತು ಬೂಲ್ ಆಗಿರಬೇಕು, '{cond_type}' ಅಲ್ಲ", node)

        true_type = self.visit(node.true_block)
        false_type = VOID
        if node.false_block:
            false_type = self.visit(node.false_block)

        return common_type(true_type, false_type)

    def visit_PostfixAction(self, node: PostfixAction) -> Type:
        # Start with the value type
        current_type = self.visit(node.value)

        # Apply each action
        for action in node.actions:
            symbol = self.symbols.lookup(action.name)
            if symbol and isinstance(symbol.type, BlockType):
                current_type = symbol.type.return_type
            else:
                current_type = ANY

        return current_type


def check_types(program: Program) -> List[TypeError]:
    """Type check a program and return errors."""
    checker = TypeChecker()
    return checker.check(program)
