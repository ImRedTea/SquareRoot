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


class SpanishTests(unittest.TestCase):
    def test_spanish_is_registered(self):
        self.assertEqual(i18n.LANGUAGES["es"], "Español")

    def test_ui_strings(self):
        self.assertEqual(i18n.translate("es", "button.evaluate"), "Calcular raíz cuadrada")
        self.assertEqual(
            i18n.translate("es", "status.precision", precision=7),
            "decimal · precisión 7",
        )

    def test_error_message_contains_position_and_localized_tokens(self):
        exc = ParseError("x", code="expected_token", expected="RPAREN", found="EOF", position=5)
        message = i18n.translate_error("es", exc)
        self.assertIn("5", message)
        self.assertIn("«)»", message)
        self.assertIn("fin de la expresión", message)


def _no_locale():
    return (None, None)


class DetectLanguageTests(unittest.TestCase):
    def detect(self, environ, getlocale=_no_locale):
        return i18n.detect_language(environ=environ, getlocale=getlocale)

    def test_each_supported_language_from_lang(self):
        for value, expected in [
            ("ru_RU.UTF-8", "ru"),
            ("en_US.UTF-8", "en"),
            ("es_ES.UTF-8", "es"),
            ("es_MX", "es"),
            ("zh_CN.UTF-8", "zh"),
            ("ja_JP.UTF-8", "ja"),
            ("EN_gb", "en"),
        ]:
            with self.subTest(value=value):
                self.assertEqual(self.detect({"LANG": value}), expected)

    def test_lc_all_beats_lc_messages_beats_lang(self):
        env = {"LC_ALL": "es_ES", "LC_MESSAGES": "en_US", "LANG": "ja_JP"}
        self.assertEqual(self.detect(env), "es")
        del env["LC_ALL"]
        self.assertEqual(self.detect(env), "en")
        del env["LC_MESSAGES"]
        self.assertEqual(self.detect(env), "ja")

    def test_c_and_posix_skip_to_next_candidate(self):
        self.assertEqual(self.detect({"LANG": "C.UTF-8"}, lambda: ("es_ES", "UTF-8")), "es")
        self.assertEqual(self.detect({"LC_ALL": "POSIX", "LANG": "zh_CN"}), "zh")

    def test_unknown_or_missing_locale_gives_default(self):
        for env in ({}, {"LANG": ""}, {"LANG": "C"}, {"LANG": "fr_FR.UTF-8"}):
            with self.subTest(env=env):
                self.assertEqual(self.detect(env), i18n.DEFAULT_LANGUAGE)

    def test_windows_style_names(self):
        for value, expected in [
            ("Russian_Russia", "ru"),
            ("English_United States", "en"),
            ("Spanish_Spain", "es"),
            ("Chinese_China", "zh"),
            ("Japanese_Japan", "ja"),
        ]:
            with self.subTest(value=value):
                self.assertEqual(self.detect({}, lambda v=value: (v, "1252")), expected)

    def test_getlocale_failure_is_ignored(self):
        def boom():
            raise ValueError("unknown locale")

        self.assertEqual(self.detect({}, boom), i18n.DEFAULT_LANGUAGE)

    def test_defaults_use_real_environment_without_raising(self):
        self.assertIn(i18n.detect_language(), i18n.LANGUAGES)


if __name__ == "__main__":
    unittest.main()
