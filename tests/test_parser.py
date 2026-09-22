import unittest

from squareroot import evaluate
from squareroot.complex_number import Complex
from squareroot.errors import ParseError, TokenizeError, UnknownFunctionError


class ParserTests(unittest.TestCase):
    def _eval(self, text):
        return evaluate(text)

    def test_precedence(self):
        self.assertEqual(self._eval("2+3*4"), Complex(14, 0))

    def test_parentheses(self):
        self.assertEqual(self._eval("(2+3)*4"), Complex(20, 0))

    def test_unary_minus(self):
        self.assertEqual(self._eval("-3+5"), Complex(2, 0))

    def test_power_right_associative(self):
        self.assertEqual(self._eval("2^3^2"), Complex(512, 0))

    def test_complex_literals_and_ops(self):
        self.assertEqual(self._eval("(1+2i)*(3-1i)"), Complex(5, 5))

    def test_sqrt_function(self):
        self.assertEqual(self._eval("sqrt(-4)"), Complex(0, 2))

    def test_conj_function(self):
        self.assertEqual(self._eval("conj(3+4i)"), Complex(3, -4))

    def test_unknown_function_raises(self):
        with self.assertRaises(UnknownFunctionError):
            self._eval("foo(1)")

    def test_invalid_character_raises_tokenize_error(self):
        with self.assertRaises(TokenizeError):
            self._eval("2 & 3")

    def test_malformed_expression_raises_parse_error(self):
        with self.assertRaises(ParseError):
            self._eval("2+*3")

    def test_unclosed_parenthesis_raises_parse_error(self):
        with self.assertRaises(ParseError):
            self._eval("(1+2")

    def test_trailing_tokens_raise_parse_error(self):
        with self.assertRaises(ParseError):
            self._eval("2 3")


if __name__ == "__main__":
    unittest.main()
