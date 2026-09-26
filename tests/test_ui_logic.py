import unittest
from unittest import mock

import squareroot
from squareroot.ui import i18n
from squareroot.ui.logic import build_variables, compute


class BuildVariablesTests(unittest.TestCase):
    def test_skips_fully_blank_row(self):
        self.assertEqual(build_variables([("", "")]), {})

    def test_skips_blank_value_with_name_present(self):
        self.assertEqual(build_variables([("a", "")]), {})

    def test_skips_blank_name_with_value_present(self):
        self.assertEqual(build_variables([("", "5")]), {})

    def test_keeps_filled_row(self):
        self.assertEqual(build_variables([("a", "-3")]), {"a": "-3"})

    def test_strips_whitespace(self):
        self.assertEqual(build_variables([("  a  ", " 5 ")]), {"a": "5"})

    def test_multiple_rows_mixed_blank(self):
        rows = [("a", "-3"), ("", ""), ("b", "2")]
        self.assertEqual(build_variables(rows), {"a": "-3", "b": "2"})

    def test_duplicate_names_last_wins(self):
        self.assertEqual(build_variables([("a", "1"), ("a", "2")]), {"a": "2"})


class ComputeNumericTests(unittest.TestCase):
    def test_simple_numeric(self):
        result = compute("-4", {}, 28)
        self.assertEqual(result.state, "numeric")
        self.assertEqual(result.header, "√(-4) =")
        self.assertEqual(result.value, "2i")

    def test_complex_literal_radicand(self):
        result = compute("3+4i", {}, 28)
        self.assertEqual(result.state, "numeric")
        self.assertEqual(result.value, "2+i")

    def test_precision_passthrough(self):
        low = compute("2", {}, 5)
        high = compute("2", {}, 25)
        self.assertNotEqual(low.value, high.value)
        self.assertGreater(len(high.value), len(low.value))


class ComputeSymbolicTests(unittest.TestCase):
    def test_symbolic_result_no_variables_bound(self):
        result = compute("a^2", {}, 28, language="en")
        self.assertEqual(result.state, "symbolic")
        self.assertEqual(result.header, "√(a^2) simplifies to")
        self.assertEqual(result.value, "abs(a)")
        self.assertIn("Provide a value", result.hint)

    def test_symbolic_becomes_numeric_when_variable_bound(self):
        result = compute("a^2", {"a": "-3"}, 28)
        self.assertEqual(result.state, "numeric")
        self.assertEqual(result.value, "3")

    def test_two_free_variables(self):
        result = compute("a^2/b^2", {}, 28)
        self.assertEqual(result.state, "symbolic")


class ComputeLanguageTests(unittest.TestCase):
    def test_default_language_is_russian(self):
        result = compute("a^2", {}, 28)
        self.assertEqual(result.header, "√(a^2) упрощается до")
        self.assertIn("Укажите значение", result.hint)

    def test_chinese_symbolic_result(self):
        result = compute("a^2", {}, 28, language="zh")
        self.assertEqual(result.header, "√(a^2) 化简为")

    def test_spanish_symbolic_result(self):
        result = compute("a^2", {}, 28, language="es")
        self.assertEqual(result.header, "√(a^2) se simplifica a")

    def test_japanese_symbolic_result(self):
        result = compute("a^2", {}, 28, language="ja")
        self.assertEqual(result.header, "√(a^2) を簡略化すると")

    def test_error_type_stable_across_languages(self):
        for language in i18n.LANGUAGES:
            result = compute("1/0", {}, 28, language=language)
            self.assertEqual(result.error_type, "DivisionByZeroError")

    def test_error_type_label_translated(self):
        ru = compute("1/0", {}, 28, language="ru")
        en = compute("1/0", {}, 28, language="en")
        self.assertEqual(ru.error_type_label, "Деление на ноль")
        self.assertEqual(en.error_type_label, "Division by zero")
        self.assertNotEqual(ru.error_type_label, en.error_type_label)


class ComputeErrorTests(unittest.TestCase):
    def test_division_by_zero_error_type(self):
        result = compute("1/0", {}, 28)
        self.assertEqual(result.state, "error")
        self.assertEqual(result.error_type, "DivisionByZeroError")
        self.assertEqual(result.header, "√(1/0)")
        self.assertEqual(result.value, "")

    def test_tokenize_error_type(self):
        result = compute("1 $ 2", {}, 28)
        self.assertEqual(result.state, "error")
        self.assertEqual(result.error_type, "TokenizeError")

    def test_parse_error_type(self):
        result = compute("1+", {}, 28)
        self.assertEqual(result.state, "error")
        self.assertEqual(result.error_type, "ParseError")


class WrappingBehaviorTests(unittest.TestCase):
    def test_radicand_containing_sqrt_is_not_double_unwrapped(self):
        result = compute("sqrt(4)", {}, 28)
        self.assertEqual(result.state, "numeric")
        expected = str(squareroot.evaluate("sqrt(sqrt(4))"))
        self.assertEqual(result.value, expected)
        self.assertNotEqual(result.value, "2")


class UnexpectedExceptionTests(unittest.TestCase):
    def test_bug_in_core_is_shown_as_localized_internal_error(self):
        with mock.patch.object(squareroot, "evaluate", side_effect=RuntimeError("boom")):
            for lang in i18n.LANGUAGES:
                with self.subTest(lang=lang):
                    result = compute("2", {}, 28, language=lang)
                    self.assertEqual(result.state, "error")
                    self.assertEqual(result.error_type, "InternalError")
                    self.assertIn("RuntimeError", result.error_message)
                    self.assertNotEqual(result.error_type_label, "InternalError")


if __name__ == "__main__":
    unittest.main()
