import unittest

from squareroot.errors import (
    DivisionByZeroError,
    ParseError,
    TokenizeError,
    UnknownFunctionError,
    UnsupportedOperationError,
)
from squareroot.ui import i18n


class TranslationCoverageTests(unittest.TestCase):
    def test_all_languages_share_the_same_keys(self):
        default_keys = set(i18n.TRANSLATIONS[i18n.DEFAULT_LANGUAGE])
        for language in i18n.LANGUAGES:
            with self.subTest(language=language):
                self.assertEqual(set(i18n.TRANSLATIONS[language]), default_keys)

    def test_all_languages_have_error_type_labels_for_every_squareroot_error(self):
        exceptions = [
            TokenizeError("x"),
            ParseError("x"),
            DivisionByZeroError("x"),
            UnknownFunctionError("x"),
            UnsupportedOperationError("x"),
        ]
        for language in i18n.LANGUAGES:
            for exc in exceptions:
                with self.subTest(language=language, exc=type(exc).__name__):
                    label = i18n.error_type_label(language, exc)
                    self.assertNotEqual(label, "")
                    self.assertNotEqual(label, type(exc).__name__)

    def test_all_languages_render_every_error_code_without_raising(self):
        cases = [
            TokenizeError("x", code="invalid_number", position=3),
            TokenizeError("x", code="unexpected_character", char="$", position=2),
            ParseError("x", code="expected_token", expected="RPAREN", found="EOF", position=5),
            ParseError("x", code="unexpected_token", found="STAR", position=1),
            UnknownFunctionError("x", code="unknown_function", name="foo"),
            DivisionByZeroError("x", code="division_by_zero"),
            DivisionByZeroError("x", code="zero_to_nonpositive_power"),
            UnsupportedOperationError("x", code="non_integer_power_complex_base"),
        ]
        for language in i18n.LANGUAGES:
            for exc in cases:
                with self.subTest(language=language, code=exc.code):
                    message = i18n.translate_error(language, exc)
                    self.assertIsInstance(message, str)
                    self.assertNotEqual(message, "")
                    self.assertNotIn("{", message)


class TranslateHelperTests(unittest.TestCase):
    def test_translate_formats_placeholders(self):
        text = i18n.translate("en", "status.precision", precision=42)
        self.assertEqual(text, "decimal · precision 42")

    def test_translate_error_falls_back_to_str_for_unknown_code(self):
        exc = DivisionByZeroError("division by zero")
        exc.code = "not_a_real_code"
        self.assertEqual(i18n.translate_error("ru", exc), "division by zero")


if __name__ == "__main__":
    unittest.main()
