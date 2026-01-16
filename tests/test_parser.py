#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser Tests
============

Test the Kapila parser.

Run from project root: python -m tests.test_parser
"""

import sys
import os
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path for running directly
if __name__ == "__main__":
    kapila_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if kapila_dir not in sys.path:
        sys.path.insert(0, kapila_dir)

from src.parser import parse, Parser
from src.parser.ast import (
    Program, WordDef, VarAssign, ExprStmt,
    NumberLit, StringLit, BoolLit, Word,
    Block, ListLit, MapLit,
    BinaryExpr, UnaryExpr, Conditional, PostfixAction,
    print_ast
)
from src.lexer import tokenize


def test_parse(name: str, source: str, expected_type=None):
    """Parse source and print AST."""
    print(f"\n=== {name} ===")
    print(f"Source: {source}")
    try:
        ast = parse(source)
        print(f"AST: {print_ast(ast)}")

        if expected_type and ast.statements:
            stmt = ast.statements[0]
            if isinstance(stmt, ExprStmt):
                assert isinstance(stmt.expr, expected_type), \
                    f"Expected {expected_type.__name__}, got {type(stmt.expr).__name__}"
            else:
                assert isinstance(stmt, expected_type), \
                    f"Expected {expected_type.__name__}, got {type(stmt).__name__}"
            print("✓ Type check passed")

        return ast
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("=" * 60)
    print("KAPILA PARSER TESTS")
    print("=" * 60)

    # Literals
    test_parse("Number literal", "೫", NumberLit)
    test_parse("Decimal number", "3.14")
    test_parse("String literal", '"ನಮಸ್ಕಾರ"', StringLit)
    test_parse("Boolean true", "ನಿಜ", BoolLit)
    test_parse("Boolean false", "ಸುಳ್ಳು", BoolLit)

    # Arithmetic
    test_parse("Addition", "೫ + ೩", BinaryExpr)
    test_parse("Multiplication", "೫ * ೧೦", BinaryExpr)
    test_parse("Complex expr", "೫ + ೩ * ೨", BinaryExpr)
    test_parse("Unary minus", "-೫", UnaryExpr)

    # Comparisons
    test_parse("Less than", "x < ೧೦", BinaryExpr)
    test_parse("Equality", "x = ೫", BinaryExpr)

    # Logical
    test_parse("And", "ನಿಜ ಮತ್ತು ಸುಳ್ಳು", BinaryExpr)
    test_parse("Or", "ನಿಜ ಅಥವಾ ಸುಳ್ಳು", BinaryExpr)

    # Assignment
    test_parse("Variable assignment", "x := ೫.", VarAssign)
    test_parse("Expression assignment", "y := ೫ * ೨.", VarAssign)

    # Word definition
    test_parse("Word definition", "square: dup * ॥", WordDef)
    test_parse("Multi-word def", "double: ೨ * ॥", WordDef)

    # Blocks (note: empty [ ] is a list, not a block)
    test_parse("Empty brackets (list)", "[ ]", ListLit)
    test_parse("Block with body", "[ dup * ]", Block)
    test_parse("Block with params", "[ x | x x * ]", Block)

    # Lists
    test_parse("List literal", "[ ೧ ೨ ೩ ]", ListLit)

    # Maps
    test_parse("Map literal", '{ ಹೆಸರು: "ರಾಮ" }', MapLit)

    # Conditional
    test_parse("Conditional", 'x > ೫ ? [ "ದೊಡ್ಡ" ] [ "ಚಿಕ್ಕ" ]', Conditional)

    # Postfix actions
    test_parse("Postfix action", "೫ ಮುದ್ರಿಸು.", PostfixAction)
    test_parse("Multiple actions", "೫ square ಮುದ್ರಿಸು.", PostfixAction)

    # Full program
    test_parse("Full program",
               '''
               square: dup * ॥
               x := ೫.
               x square ಮುದ್ರಿಸು.
               ''')

    print("\n" + "=" * 60)
    print("Tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
