"""Black-box tests of the public API.

Only `squareroot.evaluate`, `Complex`, `Expression` and the public error
classes are used -- nothing from parser/simplify internals. Expected values
come from the mathematical definition of the principal square root, not
from running the implementation. Cases are grouped by equivalence class,
with boundary values called out explicitly.
"""

import unittest

import squareroot
from squareroot import (
    Complex,
    DivisionByZeroError,
    Expression,
    ParseError,
    SquareRootError,
    TokenizeError,
    UnknownFunctionError,
    UnsupportedOperationError,
    evaluate,
)


class PerfectSquaresAndReals(unittest.TestCase):
    def test_exact_results(self):
        for expr, expected in [
            ("sqrt(0)", "0"),
            ("sqrt(1)", "1"),
            ("sqrt(4)", "2"),
            ("sqrt(144)", "12"),
            ("sqrt(0.25)", "0.5"),
            ("sqrt(1/4)", "0.5"),
            ("2^10", "1024"),
            ("  sqrt( 9 )  ", "3"),
        ]:
            with self.subTest(expr=expr):
                self.assertEqual(str(evaluate(expr)), expected)

    def test_irrational_root_default_precision(self):
        self.assertEqual(str(evaluate("sqrt(2)")), "1.414213562373095048801688724")

    def test_large_operand(self):
        result = str(evaluate("sqrt(123456789012345678901234567890)", precision=40))
        self.assertTrue(result.startswith("351364182882014.4253111222"), result)


class NegativeAndComplexRadicands(unittest.TestCase):
    def test_negative_reals_give_imaginary_roots(self):
        self.assertEqual(str(evaluate("sqrt(-4)")), "2i")
        self.assertEqual(str(evaluate("sqrt(-1)")), "i")
        self.assertEqual(str(evaluate("sqrt(-1)^2")), "-1")

    def test_complex_radicands(self):
        # (2+i)^2 = 3+4i ; (1+i)^2 = 2i
        self.assertEqual(evaluate("sqrt(3+4i)"), Complex(2, 1))
        self.assertEqual(str(evaluate("sqrt(2i)")), "1+i")

    def test_principal_branch_has_nonnegative_real_part(self):
        result = evaluate("sqrt(-4i)", precision=10)
        self.assertGreater(result.real, 0)
        self.assertLess(result.imag, 0)


class PrecisionBoundaries(unittest.TestCase):
    def test_lower_bound_one_significant_digit(self):
        self.assertEqual(str(evaluate("sqrt(2)", precision=1)), "1")

    def test_requested_precision_is_honoured(self):
        self.assertEqual(str(evaluate("sqrt(2)", precision=5)), "1.4142")

    def test_upper_bound_hundred_digits(self):
        text = str(evaluate("sqrt(2)", precision=100))
        self.assertTrue(text.startswith("1.4142135623730950488016887242096980785696718753769"))
        self.assertEqual(len(text.replace(".", "")), 100)

    def test_higher_precision_extends_lower_precision_prefix(self):
        short = str(evaluate("sqrt(3)", precision=10))
        long = str(evaluate("sqrt(3)", precision=60))
        self.assertTrue(long.startswith(short[:-1]))

    def test_precision_below_range_is_rejected(self):
        for bad in (0, -1):
            with self.subTest(precision=bad):
                with self.assertRaises(ValueError):
                    evaluate("sqrt(2)", precision=bad)

    def test_default_precision_constant(self):
        self.assertEqual(squareroot.DEFAULT_PRECISION, 28)
        self.assertEqual(
            str(evaluate("sqrt(2)")),
            str(evaluate("sqrt(2)", precision=squareroot.DEFAULT_PRECISION)),
        )


class SymbolicAndVariables(unittest.TestCase):
    def test_free_variable_stays_symbolic(self):
        result = evaluate("sqrt(a^2)")
        self.assertIsInstance(result, Expression)
        self.assertEqual(str(result), "abs(a)")
        self.assertEqual(result.variables, frozenset({"a"}))

    def test_substitution_at_call_time(self):
        self.assertEqual(str(evaluate("sqrt(a^2)", variables={"a": "3"})), "3")
        self.assertEqual(str(evaluate("sqrt(a^2)", variables={"a": "-3"})), "3")
        self.assertEqual(str(evaluate("sqrt(a*b)", variables={"a": "4", "b": "9"})), "6")

    def test_substitution_after_the_fact(self):
        result = evaluate("sqrt(a)")
        self.assertEqual(str(result.substitute({"a": "16"})), "4")

    def test_perfect_square_polynomial(self):
        # a^2 + 2a + 1 = (a+1)^2 -> sqrt = |a+1|; at a=5 that is 6
        self.assertEqual(str(evaluate("sqrt(a^2+2*a+1)", variables={"a": "5"})), "6")


class ErrorClasses(unittest.TestCase):
    """Every documented failure mode raises its own SquareRootError subclass."""

    def assertRaisesWithCode(self, exc_type, code, expr):
        with self.assertRaises(exc_type) as ctx:
            evaluate(expr)
        self.assertEqual(ctx.exception.code, code)
        self.assertIsInstance(ctx.exception, SquareRootError)

    def test_division_by_zero(self):
        self.assertRaisesWithCode(DivisionByZeroError, "division_by_zero", "1/0")

    def test_zero_to_negative_power(self):
        with self.assertRaises(DivisionByZeroError):
            evaluate("0^(-1)")

    def test_unknown_function(self):
        self.assertRaisesWithCode(UnknownFunctionError, "unknown_function", "foo(2)")

    def test_illegal_character(self):
        self.assertRaisesWithCode(TokenizeError, "unexpected_character", "2 $ 3")

    def test_unbalanced_parenthesis(self):
        self.assertRaisesWithCode(ParseError, "unexpected_token", "sqrt(")

    def test_empty_input(self):
        self.assertRaisesWithCode(ParseError, "unexpected_token", "")
        self.assertRaisesWithCode(ParseError, "unexpected_token", "   ")

    def test_trailing_garbage(self):
        with self.assertRaises(ParseError):
            evaluate("2 3")

    def test_unsupported_power(self):
        self.assertRaisesWithCode(
            UnsupportedOperationError, "non_integer_power_complex_base", "(-8)^(1/3)"
        )

    def test_error_reports_position(self):
        with self.assertRaises(TokenizeError) as ctx:
            evaluate("2 $ 3")
        self.assertEqual(ctx.exception.params["position"], 2)

    def test_garbage_never_escapes_as_a_foreign_exception(self):
        for expr in ["", "(", ")", "+", "sqrt", "sqrt()", "1..2", "i i", "@", "🙂", "1/(1-1)"]:
            with self.subTest(expr=expr):
                try:
                    evaluate(expr)
                except SquareRootError:
                    pass


class AlgebraicProperties(unittest.TestCase):
    def test_square_of_root_returns_operand_at_high_precision(self):
        for x in ("2", "7", "0.5", "123.456"):
            with self.subTest(x=x):
                root = evaluate(f"sqrt({x})", precision=50)
                squared = root * root
                self.assertEqual(round(float(squared.real), 6), float(x))

    def test_evaluation_is_deterministic(self):
        self.assertEqual(evaluate("sqrt(-7+24i)"), evaluate("sqrt(-7+24i)"))
        # (3+4i)^2 = -7+24i
        self.assertEqual(evaluate("sqrt(-7+24i)"), Complex(3, 4))


if __name__ == "__main__":
    unittest.main()
