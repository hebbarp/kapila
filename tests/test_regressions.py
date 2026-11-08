#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Discoverable regression tests for Kapila's supported execution paths."""

import contextlib
import io
import subprocess
import sys
import unittest
from pathlib import Path

from src.codegen import generate_llvm
from src.codegen.c_generator import generate_c
from src.parser import parse
from src.parser.ast import BinaryExpr, ExprStmt, NumberLit, WordDef
from src.semantic.checker import check_types
from src.vm import VM


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def run_source(source: str) -> tuple[str, VM]:
    vm = VM()
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        vm.run(source)
    return output.getvalue(), vm


class ParserAndTypeTests(unittest.TestCase):
    def test_kannada_numerals_and_precedence(self):
        program = parse("೫ + ೩ * ೨")
        expression = program.statements[0]
        self.assertIsInstance(expression, ExprStmt)
        self.assertIsInstance(expression.expr, BinaryExpr)
        self.assertEqual(expression.expr.op, "+")
        self.assertIsInstance(expression.expr.left, NumberLit)
        self.assertEqual(expression.expr.left.value, 5)
        self.assertIsInstance(expression.expr.right, BinaryExpr)

    def test_word_definition(self):
        program = parse("ವರ್ಗ: ನಕಲು * ॥")
        self.assertIsInstance(program.statements[0], WordDef)
        self.assertEqual(program.statements[0].name, "ವರ್ಗ")

    def test_valid_program_has_no_type_errors(self):
        program = parse('x := ೫. x + ೩ ಮುದ್ರಿಸು.')
        self.assertEqual(check_types(program), [])


class InterpreterTests(unittest.TestCase):
    def test_supported_languages_execute_equivalently(self):
        programs = (
            "೫ ೩ ಕೂಡು ಮುದ್ರಿಸು.",
            "५ ३ जोड़ो छापो.",
            "౫ ౩ కూడు ముద్రించు.",
        )
        for source in programs:
            with self.subTest(source=source):
                output, vm = run_source(source)
                self.assertEqual(output, "8\n")
                self.assertEqual(vm.stack, [])

    def test_kannada_reserved_words_work_as_postfix_builtins(self):
        source = "ಪಟ್ಟಿ := [ ೧ ೨ ೩ ]. ಪಟ್ಟಿ [ ಮುದ್ರಿಸು ] ಪ್ರತಿಯೊಂದಕ್ಕೂ."
        output, vm = run_source(source)
        self.assertEqual(output, "1\n2\n3\n")
        self.assertEqual(vm.stack, [])

    def test_runnable_examples(self):
        # file_processor.kpl intentionally requires a command-line file name.
        files = sorted(EXAMPLES.glob("*.kpl"))
        # mashables.kpl fetches live data; tests/test_sources.py covers it offline.
        files = [path for path in files if path.name not in ("file_processor.kpl", "mashables.kpl")]
        self.assertGreaterEqual(len(files), 12)
        for path in files:
            with self.subTest(example=path.name):
                output, _ = run_source(path.read_text(encoding="utf-8"))
                self.assertIsInstance(output, str)


class BackendTests(unittest.TestCase):
    def test_c_word_prototypes_precede_generated_blocks(self):
        prelude = (ROOT / "lib" / "prelude.kpl").read_text(encoding="utf-8")
        generated = generate_c(parse(prelude + "\n೫ ವರ್ಗ ಮುದ್ರಿಸು."))
        prototype = generated.index("void word_")
        block = generated.index("static void _block_")
        self.assertLess(prototype, block)

    def test_native_compiler_smoke(self):
        from kapilac import find_c_compiler

        compiler, _ = find_c_compiler()
        if compiler is None:
            self.skipTest("No C compiler available")
        result = subprocess.run(
            [sys.executable, str(ROOT / "kapilac.py"), "-c", "೫ ೩ ಕೂಡು ಮುದ್ರಿಸು.", "-r"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "8")

    @unittest.skipIf(generate_llvm is None, "llvmlite is not installed")
    def test_llvm_ir_smoke(self):
        generated = generate_llvm(parse("೫ ೩ ಕೂಡು ಮುದ್ರಿಸು."))
        self.assertIn('define i32 @"main"()', generated)
        self.assertIn('call void @"add_op"()', generated)


if __name__ == "__main__":
    unittest.main()


class SandboxTests(unittest.TestCase):
    def test_sandbox_blocks_file_io_in_every_language(self):
        from src.vm.builtins import UNSAFE_BUILTINS
        vm = VM(sandbox=True)
        self.assertFalse(any(f in UNSAFE_BUILTINS for f in vm.builtins.values()))
        with self.assertRaises(Exception):
            vm.run('"/etc/hostname" read-file')
        self.assertIn('read-file', VM().builtins)
