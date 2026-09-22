import unittest
from decimal import Decimal

from squareroot import evaluate
from squareroot.complex_number import Complex
from squareroot.errors import DivisionByZeroError, UnknownFunctionError
from squareroot.parser import BinOp, Call, Literal, Variable, parse
from squareroot.simplify import render, simplify, substitute


class SimplifyTests(unittest.TestCase):
    def test_variable_stays_unreduced(self):
        self.assertEqual(simplify(parse("a")), Variable("a"))

    def test_constant_folding_still_works(self):
        self.assertEqual(simplify(parse("2+3*4")), Literal(Complex(14, 0)))

    def test_additive_identities(self):
        self.assertEqual(render(simplify(parse("a+0"))), "a")
        self.assertEqual(render(simplify(parse("0+a"))), "a")
        self.assertEqual(render(simplify(parse("a-0"))), "a")
        self.assertEqual(render(simplify(parse("0-a"))), "-a")

    def test_multiplicative_identities(self):
        self.assertEqual(render(simplify(parse("a*1"))), "a")
        self.assertEqual(render(simplify(parse("1*a"))), "a")
        self.assertEqual(render(simplify(parse("a/1"))), "a")
        self.assertEqual(render(simplify(parse("a^1"))), "a")
        self.assertEqual(render(simplify(parse("+a"))), "a")

    def test_annihilation_identities(self):
        self.assertEqual(simplify(parse("a*0")), Literal(Complex(0, 0)))
        self.assertEqual(simplify(parse("0*a")), Literal(Complex(0, 0)))
        self.assertEqual(simplify(parse("a^0")), Literal(Complex(1, 0)))

    def test_zero_divided_by_variable_does_not_fold(self):
        result = simplify(parse("0/a"))
        self.assertEqual(result, BinOp("/", Literal(Complex(0, 0)), Variable("a")))
        self.assertEqual(render(result), "0/a")
        with self.assertRaises(DivisionByZeroError):
            evaluate("0/a", variables={"a": "0"})

    def test_annihilation_tradeoff_swallows_division_by_zero(self):
        # Documented tradeoff: `1/a` is discarded by `x*0 -> 0` before `a`
        # is ever bound, so this does NOT raise DivisionByZeroError.
        self.assertEqual(evaluate("(1/a)*0", variables={"a": "0"}), Complex(0, 0))

    def test_sqrt_constant(self):
        self.assertEqual(simplify(parse("sqrt(4)")), Literal(Complex(2, 0)))
        self.assertEqual(simplify(parse("sqrt(-4)")), Literal(Complex(0, 2)))

    def test_sqrt_of_even_power(self):
        self.assertEqual(render(simplify(parse("sqrt(a^2)"))), "a")

    def test_sqrt_distributes_over_product_with_constant(self):
        self.assertEqual(render(simplify(parse("sqrt(4*a^2)"))), "2*a")

    def test_sqrt_distributes_leaving_residual_sqrt(self):
        self.assertEqual(render(simplify(parse("sqrt(a^2*b)"))), "a*sqrt(b)")

    def test_sqrt_of_odd_power(self):
        self.assertEqual(render(simplify(parse("sqrt(a^3)"))), "a*sqrt(a)")

    def test_sqrt_distributes_over_quotient(self):
        self.assertEqual(render(simplify(parse("sqrt(a^2/b^2)"))), "a/b")

    def test_sqrt_of_negative_constant_times_variable_squared(self):
        self.assertEqual(render(simplify(parse("sqrt(-4*a^2)"))), "2i*a")

    def test_sqrt_of_bare_variable_unreduced(self):
        self.assertEqual(simplify(parse("sqrt(a)")), Call("sqrt", Variable("a")))

    def test_sqrt_of_sum_unreduced(self):
        result = simplify(parse("sqrt(a+b)"))
        self.assertIsInstance(result, Call)
        self.assertEqual(result.name, "sqrt")

    def test_sqrt_of_non_integer_exponent_unreduced(self):
        result = simplify(parse("sqrt(a^1.5)"))
        self.assertIsInstance(result, Call)
        self.assertEqual(result.name, "sqrt")

    def test_unknown_function_raises_even_symbolically(self):
        with self.assertRaises(UnknownFunctionError):
            simplify(parse("foo(a)"))

    def test_render_precedence_examples(self):
        self.assertEqual(
            render(simplify(parse("a^2*b"))), "a^2*b"
        )
        self.assertEqual(
            render(simplify(parse("(a+b)^2"))), "(a+b)^2"
        )
        self.assertEqual(
            render(simplify(parse("(-3)^a"))), "(-3)^a"
        )

    def test_substitute_partial_binding(self):
        node = substitute(parse("a+b"), {"a": Complex(3, 0)})
        self.assertEqual(render(simplify(node)), "3+b")


if __name__ == "__main__":
    unittest.main()
