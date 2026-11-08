# -*- coding: utf-8 -*-
"""The compiler must build what was written or refuse. It must never skip."""

import contextlib
import io
import subprocess
import sys
import unittest
from pathlib import Path

from src.codegen.c_generator import CompileError, generate_c
from src.parser import parse
from src.vm import VM, KapilaError

ROOT = Path(__file__).resolve().parent.parent


def compile_only(code):
    return generate_c(parse(code))


class CompileErrors(unittest.TestCase):
    def assert_refused(self, code, *fragments, line=None):
        with self.assertRaises(CompileError) as ctx:
            compile_only(code)
        for fragment in fragments:
            self.assertIn(fragment, str(ctx.exception))
        if line is not None:
            self.assertEqual(ctx.exception.line, line)

    def test_unknown_word_is_refused_with_its_line(self):
        self.assert_refused('೧ ಮುದ್ರಿಸು.\nಗೊತ್ತಿಲ್ಲ ಮುದ್ರಿಸು.', 'ಗೊತ್ತಿಲ್ಲ', line=2)

    def test_interpreter_only_word_says_so(self):
        self.assert_refused('"ಮೈಸೂರು" ಹವಾಮಾನ ಮುದ್ರಿಸು.', 'ಹವಾಮಾನ', 'interpreter')

    def test_records_are_refused(self):
        self.assert_refused('ದ := { ಎ: ೧ }.', 'interpreter')

    def test_equals_suggests_assignment(self):
        self.assert_refused('ಅ = ೨.', ':=')

    def test_equals_on_a_known_variable_is_comparison(self):
        self.assertIn('eq_op', compile_only('ಅ := ೨.\nಅ = ೨ ಮುದ್ರಿಸು.'))

    def test_word_may_use_a_variable_another_word_assigns(self):
        compile_only('ಓದು: ಅ ಮುದ್ರಿಸು ॥\nಬರೆ: ಅ := ೫. ॥\nಬರೆ ಓದು.')


class VerbLastAssignment(unittest.TestCase):
    def setUp(self):
        from kapilac import find_c_compiler
        if find_c_compiler()[0] is None:
            self.skipTest("no C compiler")

    def run_compiled(self, code):
        result = subprocess.run(
            [sys.executable, str(ROOT / "kapilac.py"), "-c", code, "-r"],
            capture_output=True, encoding="utf-8", errors="replace", timeout=60,
            cwd=ROOT,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()

    def test_cases_match_the_interpreter(self):
        cases = {
            'verb last': 'ಅ := ೨ ೩ ಕೂಡು.\nಅ ಮುದ್ರಿಸು.',
            'infix': 'ಅ := ೨ + ೩.\nಅ ಮುದ್ರಿಸು.',
            'operator last': 'ಅ := ೨ ೩ +.\nಅ ಮುದ್ರಿಸು.',
            'mid-chain variable': 'ಬ := ೪.\nಅ := ಬ ೩ ಗುಣಿಸು.\nಅ ಮುದ್ರಿಸು.',
            'higher order': 'ಪ := [ ೧ ೨ ] [ ೨ ಗುಣಿಸು ] ನಕ್ಷೆ.\nಪ ಮುದ್ರಿಸು.',
            'no full stop': 'ಅ := ೭\nಅ ಮುದ್ರಿಸು.',
            'two on a line': 'ಅ := ೧. ಬ := ೨ ೩ ಕೂಡು. ಬ ಮುದ್ರಿಸು.',
        }
        for name, code in cases.items():
            with self.subTest(name):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    VM(sandbox=True).run(code)
                rc, compiled, err = self.run_compiled(code)
                self.assertEqual(rc, 0, err)
                # the C runtime prints lists without commas
                self.assertEqual(compiled, out.getvalue().strip().replace(',', ''))

    def test_refusal_reports_the_users_line_not_the_preludes(self):
        rc, _, err = self.run_compiled('೧ ಮುದ್ರಿಸು.\nಗೊತ್ತಿಲ್ಲ.')
        self.assertEqual(rc, 1)
        self.assertIn('<code>:2:', err)


class InterpreterHint(unittest.TestCase):
    def test_equals_suggests_assignment(self):
        with self.assertRaises(KapilaError) as ctx:
            VM(sandbox=True).run('ಅ = ೨ ೩ ಕೂಡಿಸು')
        self.assertIn(':=', str(ctx.exception))

    def test_plain_unknown_word_has_no_hint(self):
        with self.assertRaises(KapilaError) as ctx:
            VM(sandbox=True).run('ಅ ಮುದ್ರಿಸು.')
        self.assertNotIn(':=', str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
