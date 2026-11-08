# -*- coding: utf-8 -*-
"""Records: literals, field access (words and genitive), sorting, printing, assignment."""

import contextlib
import io
import unittest

from src.vm import VM, KapilaError


def run(source):
    vm = VM()
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        vm.run(source)
    return out.getvalue().strip(), vm


PEOPLE = 'ಜನ := [ { ಹೆಸರು: "ಅ" ವಯಸ್ಸು: ೩ } { ಹೆಸರು: "ಬ" ವಯಸ್ಸು: ೧ } ].\n'


class RecordTests(unittest.TestCase):
    def test_genitive_field_access(self):
        out, _ = run('ಪುಸ್ತಕ := { ಲೇಖಕ: "ಕುವೆಂಪು" }. ಪುಸ್ತಕದ ಲೇಖಕ ಮುದ್ರಿಸು.')
        self.assertEqual(out, "ಕುವೆಂಪು")

    def test_genitive_forms(self):
        # ಸುದ್ದಿಯ → ಸುದ್ದಿ, ಊರಿನ → ಊರು, ಸುದ್ದಿಗಳ → ಸುದ್ದಿಗಳು
        out, _ = run('ಊರು := { ಹೆಸರು: "ಮೈಸೂರು" }. ಊರಿನ ಹೆಸರು ಮುದ್ರಿಸು.')
        self.assertEqual(out, "ಮೈಸೂರು")
        out, _ = run('ಸುದ್ದಿಗಳು := [ { ಶೀರ್ಷಿಕೆ: "ಒಂದು" } { ಶೀರ್ಷಿಕೆ: "ಎರಡು" } ]. ಸುದ್ದಿಗಳ ಶೀರ್ಷಿಕೆ ಮುದ್ರಿಸು.')
        self.assertEqual(out, "ಒಂದು\nಎರಡು")

    def test_get_with_english_alias(self):
        out, _ = run('ದ := { ಶೀರ್ಷಿಕೆ: "x" }. ದ "title" ಪಡೆ ಮುದ್ರಿಸು.')
        self.assertEqual(out, "x")

    def test_get_plucks_from_list(self):
        out, _ = run(PEOPLE + 'ಜನ "ಹೆಸರು" ಪಡೆ ಮುದ್ರಿಸು.')
        self.assertEqual(out, "ಅ\nಬ")

    def test_set_returns_new_record(self):
        _, vm = run('ದ := { ಎ: ೧ }. ಹೊಸ := ದ "ಬಿ" ೨ ಇಡು.')
        self.assertEqual(vm.variables["ಹೊಸ"], {"ಎ": 1, "ಬಿ": 2})
        self.assertEqual(vm.variables["ದ"], {"ಎ": 1})

    def test_keys_and_values(self):
        out, _ = run('ದ := { ಎ: ೧ ಬಿ: ೨ }. ದ ಕೀಲಿಗಳು ಮುದ್ರಿಸು. ದ ಮೌಲ್ಯಗಳು ಮುದ್ರಿಸು.')
        self.assertEqual(out, "ಎ\nಬಿ\n[1, 2]")

    def test_sort_by_field(self):
        _, vm = run(PEOPLE + 'ಕ್ರಮ := ಜನ "ವಯಸ್ಸು" ಅನುಸಾರ.')
        self.assertEqual([r["ಹೆಸರು"] for r in vm.variables["ಕ್ರಮ"]], ["ಬ", "ಅ"])

    def test_filter_records(self):
        _, vm = run(PEOPLE + 'ಹಿರಿಯರು := ಜನ [ "ವಯಸ್ಸು" ಪಡೆ ೨ > ] ಸೋಸು.')
        self.assertEqual(vm.variables["ಹಿರಿಯರು"], [{"ಹೆಸರು": "ಅ", "ವಯಸ್ಸು": 3}])

    def test_missing_field_is_an_error(self):
        with self.assertRaises(KapilaError) as cm:
            run('ದ := { ಎ: ೧ }. ದ "ಸಿ" ಪಡೆ.')
        self.assertIn("ಸಿ", str(cm.exception))

    def test_record_prints_one_field_per_line(self):
        out, _ = run('{ ಶೀರ್ಷಿಕೆ: "ಮಳೆ" ಮೂಲ: "ಪ್ರಜಾವಾಣಿ" } ಮುದ್ರಿಸು.')
        self.assertEqual(out, "ಶೀರ್ಷಿಕೆ: ಮಳೆ\nಮೂಲ: ಪ್ರಜಾವಾಣಿ")

    def test_plain_values_print_as_before(self):
        out, _ = run('[ ೧ ೨ ೩ ] ಮುದ್ರಿಸು.')
        self.assertEqual(out, "[1, 2, 3]")


class AssignmentTests(unittest.TestCase):
    def test_assignment_takes_postfix_result(self):
        _, vm = run('x := ೨ ೩ ಕೂಡು.')
        self.assertEqual(vm.variables["x"], 5)

    def test_assignment_can_use_values_already_on_the_stack(self):
        _, vm = run('{ ಶೀರ್ಷಿಕೆ: "x" }. r := "title" ಪಡೆ.')
        self.assertEqual(vm.variables["r"], "x")

    def test_infix_assignment_unchanged(self):
        _, vm = run('x := ೧೦. y := x + ೫.')
        self.assertEqual(vm.variables["y"], 15)

    def test_assignment_without_full_stop_ends_at_line_break(self):
        out, vm = run('nums := [ 1 2 3 ]\nnums [ dup + ] map ಮುದ್ರಿಸು.')
        self.assertEqual(vm.variables["nums"], [1, 2, 3])
        self.assertEqual(out, "[2, 4, 6]")


if __name__ == "__main__":
    unittest.main()


class BareFieldTests(unittest.TestCase):
    def test_bare_field_name_after_a_record(self):
        out, _ = run('{ ಸ್ಥಿತಿ: "ಮೋಡ" } ಸ್ಥಿತಿ ಮುದ್ರಿಸು.')
        self.assertEqual(out, "ಮೋಡ")

    def test_unknown_word_without_a_record_is_still_an_error(self):
        with self.assertRaises(KapilaError):
            run('೫ ಸ್ಥಿತಿ ಮುದ್ರಿಸು.')
