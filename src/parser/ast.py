# -*- coding: utf-8 -*-
"""
Kapila AST Node Definitions
===========================

Abstract Syntax Tree nodes for the Kapila language.

The AST represents the hierarchical structure of a Kapila program:
- Program contains Statements
- Statements can be Definitions, Assignments, or Expressions
- Expressions can be literals, operations, blocks, conditionals
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Union
from abc import ABC, abstractmethod


# === Base Classes ===

@dataclass
class Node(ABC):
    """Base class for all AST nodes."""
    line: int = 0
    column: int = 0


@dataclass
class Expr(Node):
    """Base class for expressions (things that produce values)."""
    pass


@dataclass
class Stmt(Node):
    """Base class for statements (things that do actions)."""
    pass


# === Literal Expressions ===

@dataclass
class NumberLit(Expr):
    """Numeric literal: ೫, 42, ೩.೧೪"""
    value: Union[int, float] = 0


@dataclass
class StringLit(Expr):
    """String literal: "ನಮಸ್ಕಾರ" """
    value: str = ""


@dataclass
class BoolLit(Expr):
    """Boolean literal: ನಿಜ/true, ಸುಳ್ಳು/false"""
    value: bool = False


# === Identifiers and References ===

@dataclass
class Word(Expr):
    """
    A word/identifier: ಮುದ್ರಿಸು, dup, ಅದು

    Words can be:
    - Variable references
    - Built-in operations
    - User-defined words
    """
    name: str = ""


@dataclass
class QuotedWord(Expr):
    """
    A quoted word (symbol): 'ಹೆಸರು

    Pushes the word itself as data, not its value.
    """
    name: str = ""


# === Compound Expressions ===

@dataclass
class Block(Expr):
    """
    A block of code: [ x y | x y + ]

    Blocks are first-class values that can be:
    - Passed to higher-order functions
    - Stored in variables
    - Executed with `ಕರೆ` (call)
    """
    params: List[str] = field(default_factory=list)
    body: List[Union[Expr, 'Stmt']] = field(default_factory=list)


@dataclass
class ListLit(Expr):
    """
    List literal: [ ೧ ೨ ೩ ]

    When [ ] contains only values (no words), it's a list.
    """
    elements: List[Expr] = field(default_factory=list)


@dataclass
class MapLit(Expr):
    """
    Map literal: { ಹೆಸರು: "ರಾಮ" ವಯಸ್ಸು: ೨೫ }
    """
    pairs: List[tuple] = field(default_factory=list)  # List of (key, value)


# === Binary and Unary Expressions ===

@dataclass
class BinaryExpr(Expr):
    """
    Binary operation: ೫ + ೩, x > ೧೦

    Used for infix arithmetic and comparisons.
    """
    left: Expr = None
    op: str = ""  # +, -, *, /, %, =, !=, <, >, <=, >=, ಮತ್ತು, ಅಥವಾ
    right: Expr = None


@dataclass
class UnaryExpr(Expr):
    """
    Unary operation: -೫, ಅಲ್ಲ ನಿಜ
    """
    op: str = ""  # -, ಅಲ್ಲ/not
    operand: Expr = None


# === Conditional ===

@dataclass
class Conditional(Expr):
    """
    Conditional expression: x > ೫ ? [ "ದೊಡ್ಡ" ] [ "ಚಿಕ್ಕ" ]

    If condition is true, execute true_block, else execute false_block.
    """
    condition: Expr = None
    true_block: Block = None
    false_block: Optional[Block] = None


# === Postfix Actions ===

@dataclass
class PostfixAction(Expr):
    """
    A sequence of value followed by words (postfix actions).

    Example: ೫ square ಮುದ್ರಿಸು
    - value: NumberLit(5)
    - actions: [Word("square"), Word("ಮುದ್ರಿಸು")]
    """
    value: Expr = None
    actions: List[Word] = field(default_factory=list)


# === Statements ===

@dataclass
class WordDef(Stmt):
    """
    Word definition: square: dup * ॥

    Defines a new word (function) that can be called.
    """
    name: str = ""
    body: List[Union[Expr, Stmt]] = field(default_factory=list)


@dataclass
class VarAssign(Stmt):
    """
    Variable assignment: x := ೫ * ೨.

    Binds a value to a name.
    """
    name: str = ""
    value: Expr = None


@dataclass
class ExprStmt(Stmt):
    """
    Expression statement: an expression executed for its effect.

    Example: ೫ ಮುದ್ರಿಸು.
    """
    expr: Expr = None


# === Program ===

@dataclass
class Program(Node):
    """
    Root node: a complete Kapila program.

    Contains a list of top-level statements.
    """
    statements: List[Stmt] = field(default_factory=list)


# === Visitor Pattern (for later phases) ===

class NodeVisitor(ABC):
    """
    Base class for AST visitors.

    Subclass this for:
    - Type checking (semantic analysis)
    - Code generation (LLVM IR)
    - Pretty printing
    """

    def visit(self, node: Node) -> Any:
        """Dispatch to appropriate visit method."""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: Node) -> Any:
        """Called if no explicit visitor method exists."""
        raise NotImplementedError(f"No visit method for {type(node).__name__}")


# === Pretty Printer (for debugging) ===

class ASTPrinter(NodeVisitor):
    """Print AST in a readable format."""

    def __init__(self):
        self.indent = 0

    def _indent(self) -> str:
        return "  " * self.indent

    def visit_Program(self, node: Program) -> str:
        lines = ["Program:"]
        self.indent += 1
        for stmt in node.statements:
            lines.append(self._indent() + self.visit(stmt))
        self.indent -= 1
        return "\n".join(lines)

    def visit_WordDef(self, node: WordDef) -> str:
        body = " ".join(self.visit(x) for x in node.body)
        return f"WordDef({node.name}: {body})"

    def visit_VarAssign(self, node: VarAssign) -> str:
        return f"VarAssign({node.name} := {self.visit(node.value)})"

    def visit_ExprStmt(self, node: ExprStmt) -> str:
        return f"ExprStmt({self.visit(node.expr)})"

    def visit_NumberLit(self, node: NumberLit) -> str:
        return f"Num({node.value})"

    def visit_StringLit(self, node: StringLit) -> str:
        return f"Str({node.value!r})"

    def visit_BoolLit(self, node: BoolLit) -> str:
        return f"Bool({node.value})"

    def visit_Word(self, node: Word) -> str:
        return f"Word({node.name})"

    def visit_QuotedWord(self, node: QuotedWord) -> str:
        return f"Quote({node.name})"

    def visit_Block(self, node: Block) -> str:
        params = " ".join(node.params) + " |" if node.params else ""
        body = " ".join(self.visit(x) for x in node.body)
        return f"Block([{params} {body}])"

    def visit_ListLit(self, node: ListLit) -> str:
        elems = " ".join(self.visit(e) for e in node.elements)
        return f"List([{elems}])"

    def visit_MapLit(self, node: MapLit) -> str:
        pairs = " ".join(f"{k}: {self.visit(v)}" for k, v in node.pairs)
        return f"Map({{{pairs}}})"

    def visit_BinaryExpr(self, node: BinaryExpr) -> str:
        return f"({self.visit(node.left)} {node.op} {self.visit(node.right)})"

    def visit_UnaryExpr(self, node: UnaryExpr) -> str:
        return f"({node.op} {self.visit(node.operand)})"

    def visit_Conditional(self, node: Conditional) -> str:
        cond = self.visit(node.condition)
        true_b = self.visit(node.true_block)
        false_b = self.visit(node.false_block) if node.false_block else "none"
        return f"Cond({cond} ? {true_b} : {false_b})"

    def visit_PostfixAction(self, node: PostfixAction) -> str:
        val = self.visit(node.value)
        acts = " ".join(self.visit(a) for a in node.actions)
        return f"Postfix({val} {acts})"


def print_ast(node: Node) -> str:
    """Pretty-print an AST node."""
    return ASTPrinter().visit(node)
