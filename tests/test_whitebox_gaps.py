"""White-box tests aimed at branches the module tests left uncovered
(see `coverage report`): operand coercion errors, reflected operators,
special-case power rules, Expression dunder methods and expression rendering.
"""

import unittest
from decimal import Decimal

from squareroot import Complex, DivisionByZeroError, Expression, evaluate


class ComplexCoercion(unittest.TestCase):
    def test_rejects_bool_float_and_unknown_types(self):
        for bad in (True, 1.5, None, [1]):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    Complex(1, 0) + bad

    def test_accepts_int_str_decimal(self):
        self.assertEqual(Complex(1, 0) + 2, Complex(3, 0))
        self.assertEqual(Complex(1, 0) + "2", Complex(3, 0))
        self.assertEqual(Complex(1, 0) + Decimal("0.5"), Complex("1.5", 0))

    def test_empty_string_literal_rejected(self):
        with self.assertRaises(ValueError):
            Complex.from_str("  ")


class ComplexOperators(unittest.TestCase):
    def test_reflected_operators(self):
        self.assertEqual(5 - Complex(2, 1), Complex(3, -1))
        self.assertEqual(1 / Complex(0, 1), Complex(0, -1))

    def test_unary_operators(self):
        self.assertEqual(-Complex(1, -2), Complex(-1, 2))
        self.assertEqual(+Complex(1, -2), Complex(1, -2))

    def test_zero_power_special_cases(self):
        self.assertEqual(Complex(2, 1) ** 0, Complex(1, 0))
        self.assertEqual(Complex(0, 0) ** Complex(3, 0), Complex(0, 0))
        with self.assertRaises(DivisionByZeroError):
            Complex(0, 0) ** Complex(-3, 0)

    def test_negative_integer_power(self):
        self.assertEqual(Complex(0, 1) ** -1, Complex(0, -1))

    def test_equality_and_hash(self):
        self.assertEqual(Complex(2, 0), 2)
        self.assertEqual(Complex(2, 0), "2")
        self.assertNotEqual(Complex(2, 0), None)
        self.assertNotEqual(Complex(2, 0), 2.0)
        self.assertEqual(hash(Complex(2, 1)), hash(Complex(2, 1)))
        self.assertEqual(len({Complex(1, 1), Complex(1, 1)}), 1)

    def test_repr_and_str(self):
        self.assertTrue(repr(Complex(1, 2)).startswith("Complex("))
        self.assertEqual(str(Complex("1.500", 0)), "1.5")
        self.assertEqual(str(Complex(100, 0)), "100")


class ExpressionObject(unittest.TestCase):
    def test_repr_eq_hash(self):
        a, b = evaluate("sqrt(x)"), evaluate("sqrt(x)")
        self.assertEqual(repr(a), "Expression('sqrt(x)')")
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(a, evaluate("sqrt(y)"))
        self.assertNotEqual(a, "sqrt(x)")

    def test_variables_and_substitute_keep_partial_symbolic(self):
        expr = evaluate("sqrt(x*y)")
        self.assertEqual(expr.variables, frozenset({"x", "y"}))
        partial = expr.substitute({"x": "4"})
        self.assertIsInstance(partial, Expression)
        self.assertEqual(partial.variables, frozenset({"y"}))
        self.assertEqual(partial.substitute({"y": "9"}), Complex(6, 0))


class SimplifyAndRender(unittest.TestCase):
    """Rendering/simplification of symbolic results (checked via str())."""

    def s(self, text):
        return str(evaluate(text))

    def test_unary(self):
        self.assertEqual(self.s("+x"), "x")
        self.assertEqual(self.s("-x"), "-x")
        self.assertEqual(self.s("-(x+1)"), "-(x+1)")
        self.assertEqual(self.s("-(3)"), "-3")

    def test_identity_rules(self):
        self.assertEqual(self.s("x+0"), "x")
        self.assertEqual(self.s("0+x"), "x")
        self.assertEqual(self.s("x-0"), "x")
        self.assertEqual(self.s("0-x"), "-x")
        self.assertEqual(self.s("x*1"), "x")
        self.assertEqual(self.s("1*x"), "x")
        self.assertEqual(self.s("x/1"), "x")
        self.assertEqual(self.s("x^1"), "x")
        self.assertEqual(self.s("x^0"), "1")

    def test_zero_over_symbol_is_not_folded(self):
        self.assertEqual(self.s("0/x"), "0/x")

    def test_parenthesisation_in_render(self):
        self.assertEqual(self.s("(x+1)*y"), "(x+1)*y")
        self.assertEqual(self.s("x-(y-1)"), "x-(y-1)")
        self.assertEqual(self.s("x/(y*z)"), "x/(y*z)")
        self.assertEqual(self.s("(x^y)^z"), "(x^y)^z")
        self.assertEqual(self.s("x^(y+1)"), "x^(y+1)")
        self.assertEqual(self.s("(1+2i)*x"), "(1+2i)*x")

    def test_substitution_into_every_node_kind(self):
        result = evaluate("sqrt(-x + (x+1)^2 - x/2)", variables={"x": "2"})
        self.assertEqual(result, evaluate("sqrt(6)"))


if __name__ == "__main__":
    unittest.main()
