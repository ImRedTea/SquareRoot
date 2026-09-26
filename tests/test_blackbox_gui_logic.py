"""Black-box tests of the GUI's logic layer (`ui.logic.compute`).

Input is what a user types (radicand, variable rows, precision, language);
output is what the UI shows. No Tk and no internals of the parser/evaluator.
"""

import time
import unittest

from squareroot.ui import i18n
from squareroot.ui.logic import build_variables, compute

LANGS = list(i18n.LANGUAGES)


class NumericResults(unittest.TestCase):
    def test_result_is_language_independent(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                result = compute("-4", {}, 28, language=lang)
                self.assertEqual(result.state, "numeric")
                self.assertEqual(result.header, "√(-4) =")
                self.assertEqual(result.value, "2i")
                self.assertEqual(result.error_message, "")

    def test_precision_controls_digits(self):
        self.assertEqual(compute("2", {}, 5).value, "1.4142")
        self.assertEqual(len(compute("2", {}, 100).value.replace(".", "")), 100)

    def test_variables_from_ui_rows(self):
        variables = build_variables([("a", " 9 "), ("", "1"), ("b", "")])
        self.assertEqual(variables, {"a": "9"})
        self.assertEqual(compute("a", variables, 28).value, "3")


class SymbolicResults(unittest.TestCase):
    def test_localized_header_and_hint_for_every_language(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                result = compute("a^2", {}, 28, language=lang)
                self.assertEqual(result.state, "symbolic")
                self.assertEqual(result.value, "abs(a)")
                self.assertTrue(result.header.startswith("√(a^2)"))
                self.assertNotEqual(result.hint, "")

    def test_headers_differ_between_languages(self):
        headers = {compute("a^2", {}, 28, language=l).header for l in LANGS}
        self.assertEqual(len(headers), len(LANGS))


class ErrorResults(unittest.TestCase):
    CASES = {
        "1/0": "DivisionByZeroError",
        "foo(2)": "UnknownFunctionError",
        "2 $ 3": "TokenizeError",
        "(": "ParseError",
        "(-8)^(1/3)": "UnsupportedOperationError",
        "9^9^9^9": "NumberOverflowError",
        "(" * 2000 + "1" + ")" * 2000: "ExpressionTooComplexError",
        "1+" * 3000 + "1": "ExpressionTooComplexError",
    }

    def test_each_error_is_localized_in_every_language(self):
        for expr, error_type in self.CASES.items():
            labels = set()
            for lang in LANGS:
                with self.subTest(expr=expr, lang=lang):
                    result = compute(expr, {}, 28, language=lang)
                    self.assertEqual(result.state, "error")
                    self.assertEqual(result.error_type, error_type)
                    self.assertNotEqual(result.error_message, "")
                    self.assertNotIn("{", result.error_message)
                    labels.add(result.error_type_label)
            self.assertEqual(len(labels), len(LANGS))

    def test_parse_error_never_shows_raw_token_ids(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                message = compute("(", {}, 28, language=lang).error_message
                for raw in ("RPAREN", "EOF", "LPAREN", "IDENT"):
                    self.assertNotIn(raw, message)

    def test_unknown_language_falls_back_to_default(self):
        fallback = compute("1/0", {}, 28, language="xx")
        default = compute("1/0", {}, 28, language=i18n.DEFAULT_LANGUAGE)
        self.assertEqual(fallback, default)


class FaultTolerance(unittest.TestCase):
    def test_bad_variable_value_is_a_localized_error(self):
        for value in ("abc", "nan", "inf", "1,5"):
            for lang in LANGS:
                with self.subTest(value=value, lang=lang):
                    result = compute("x", build_variables([("x", value)]), 28, language=lang)
                    self.assertEqual(result.state, "error")
                    self.assertEqual(result.error_type, "InvalidVariableValueError")
                    self.assertIn("x", result.error_message)

    def test_complex_variable_value_from_ui_row(self):
        result = compute("x", build_variables([("x", "-7+24i")]), 28)
        self.assertEqual((result.state, result.value), ("numeric", "3+4i"))

    def test_huge_power_answers_quickly(self):
        started = time.monotonic()
        result = compute("1^100000000 + 3", {}, 28)
        self.assertEqual((result.state, result.value), ("numeric", "2"))
        self.assertLess(time.monotonic() - started, 5)

    def test_invalid_precision_is_an_error_not_an_exception(self):
        result = compute("2", {}, 0, language="en")
        self.assertEqual(result.error_type, "InvalidPrecisionError")
        self.assertIn("1", result.error_message)


if __name__ == "__main__":
    unittest.main()


class ExactFormInGui(unittest.TestCase):
    def test_irrational_root_shows_closed_form(self):
        self.assertEqual(compute("8", {}, 28).exact, "2√2")
        self.assertEqual(compute("x", {"x": "-12"}, 28).exact, "2i√3")

    def test_rational_symbolic_and_error_results_have_none(self):
        self.assertEqual(compute("16", {}, 28).exact, "")
        self.assertEqual(compute("x", {}, 28).exact, "")
        self.assertEqual(compute("1/0", {}, 28).exact, "")

    def test_gui_accepts_full_api_precision_range(self):
        self.assertEqual(len(compute("2", {}, 1000).value.replace(".", "")), 1000)
