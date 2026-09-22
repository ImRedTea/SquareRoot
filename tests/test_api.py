import unittest
from decimal import Decimal

from squareroot import Complex, Expression, evaluate
from squareroot.errors import DivisionByZeroError, ParseError, TokenizeError, UnknownFunctionError


class ApiTests(unittest.TestCase):
    def test_basic_arithmetic(self):
        self.assertEqual(evaluate("1+1"), Complex(2, 0))

    def test_complex_expression(self):
        self.assertEqual(evaluate("sqrt(-4)+2i*(1-i)"), Complex(2, 4))

    def test_division_by_zero_propagates(self):
        with self.assertRaises(DivisionByZeroError):
            evaluate("1/0")

    def test_tokenize_error_propagates(self):
        with self.assertRaises(TokenizeError):
            evaluate("1 $ 2")

    def test_parse_error_propagates(self):
        with self.assertRaises(ParseError):
            evaluate("1+")

    def test_result_is_decimal_backed(self):
        result = evaluate("1/3")
        self.assertIsInstance(result.real, Decimal)
        self.assertIsInstance(result.imag, Decimal)

    def test_precision_controls_significant_digits(self):
        low = evaluate("1/3", precision=5)
        high = evaluate("1/3", precision=20)
        self.assertEqual(str(low.real), "0.33333")
        self.assertEqual(str(high.real), "0.33333333333333333333")

    def test_precision_does_not_leak_between_calls(self):
        evaluate("1/3", precision=5)
        result = evaluate("1/3")
        default_precision_result = evaluate("1/3")
        self.assertEqual(result, default_precision_result)
        self.assertEqual(len(str(result.real).replace("0.", "")), 28)

    def test_back_compat_returns_plain_complex(self):
        self.assertIs(type(evaluate("1+1")), Complex)

    def test_bare_variable_expression_is_symbolic(self):
        result = evaluate("a^2")
        self.assertIsInstance(result, Expression)
        self.assertEqual(str(result), "a^2")

    def test_sqrt_of_variable_squared_is_symbolic(self):
        result = evaluate("sqrt(a^2)")
        self.assertIsInstance(result, Expression)
        self.assertEqual(str(result), "a")

    def test_variable_substitution_collapses_to_complex(self):
        result = evaluate("a^2", variables={"a": "3"})
        self.assertEqual(result, Complex(9, 0))
        self.assertIs(type(result), Complex)

    def test_sqrt_substitution_collapses_to_complex(self):
        self.assertEqual(evaluate("sqrt(a^2)", variables={"a": "3"}), Complex(3, 0))

    def test_documented_sign_discrepancy_for_negative_substitution(self):
        # sqrt(x^2) -> x is a formal symbolic convention, not the true
        # principal value; it disagrees in sign with direct numeric sqrt
        # for negative substitutions. See squareroot/simplify.py docstring.
        self.assertEqual(evaluate("sqrt(a^2)", variables={"a": "-3"}), Complex(-3, 0))
        self.assertEqual(evaluate("sqrt(9)"), Complex(3, 0))

    def test_float_variable_value_rejected(self):
        with self.assertRaises(TypeError):
            evaluate("a", variables={"a": 1.5})

    def test_partial_multi_variable_binding_stays_symbolic(self):
        result = evaluate("a+b", variables={"a": "1"})
        self.assertIsInstance(result, Expression)
        self.assertEqual(str(result), "1+b")

    def test_unbound_variable_is_not_an_error(self):
        result = evaluate("a+1")
        self.assertIsInstance(result, Expression)

    def test_unknown_function_raises_even_with_symbolic_argument(self):
        with self.assertRaises(UnknownFunctionError):
            evaluate("foo(a)")

    def test_precision_applies_through_substitution(self):
        result = evaluate("a/3", variables={"a": "1"}, precision=5)
        self.assertEqual(str(result.real), "0.33333")

    def test_variable_values_accept_int_str_decimal_complex(self):
        expected = Complex(5, 0)
        self.assertEqual(evaluate("a", variables={"a": 5}), expected)
        self.assertEqual(evaluate("a", variables={"a": "5"}), expected)
        self.assertEqual(evaluate("a", variables={"a": Decimal("5")}), expected)
        self.assertEqual(evaluate("a", variables={"a": Complex(5, 0)}), expected)


if __name__ == "__main__":
    unittest.main()
