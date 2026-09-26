"""exact_sqrt: white box (branches) + black box (values checked by squaring)."""

import unittest
from decimal import Decimal
from fractions import Fraction

from squareroot import evaluate, exact_sqrt
from squareroot.exact import _split_square, exact_sqrt_of_rational


class ExactSqrtBlackBox(unittest.TestCase):
    CASES = {
        "8": "2√2",
        "2": "√2",
        "12*12*7": "12√7",
        "-8": "2i√2",
        "-2": "i√2",
        "1/2": "√2/2",
        "0.75": "√3/2",
        "2^5/3": "4√6/3",
        "-(3)": "i√3",
        "+5": "√5",
        "18 - 0": "3√2",
        "2^-1": "√2/2",
    }

    def test_known_closed_forms(self):
        for radicand, expected in self.CASES.items():
            with self.subTest(radicand=radicand):
                self.assertEqual(exact_sqrt(radicand), expected)

    def test_closed_form_matches_decimal_result(self):
        # a√b/q must numerically equal evaluate("sqrt(r)") to 40 digits
        for radicand in ("8", "1/2", "0.75", "2^5/3", "12*12*7", "1000001"):
            form = exact_sqrt(radicand)
            coef, _, rest = form.partition("√")
            b, _, q = rest.partition("/")
            expr = f"{coef or 1}*sqrt({b})/{q or 1}"
            diff = evaluate(expr, precision=50) - evaluate(f"sqrt({radicand})", precision=50)
            self.assertLess(abs(diff.real), Decimal("1E-40"))
            self.assertEqual(diff.imag, 0)

    def test_rational_roots_have_no_closed_form(self):
        for radicand in ("4", "0", "9/16", "0.25", "-4"):
            with self.subTest(radicand=radicand):
                self.assertIsNone(exact_sqrt(radicand))

    def test_unsupported_inputs_return_none_never_raise(self):
        for radicand in ("x", "3+4i", "sqrt(2)", "10^100", "2^1000", "1/0", "0^-1",
                         "2^(1/2)", "(((", "$", "", "2^0.5", "abs(8)"):
            with self.subTest(radicand=radicand):
                self.assertIsNone(exact_sqrt(radicand))

    def test_variables(self):
        self.assertEqual(exact_sqrt("x", {"x": "18"}), "3√2")
        self.assertEqual(exact_sqrt("x*y", {"x": "2", "y": "-1"}), "i√2")
        self.assertIsNone(exact_sqrt("x", {"x": "abc"}))
        self.assertIsNone(exact_sqrt("x", {"x": "nan"}))


class ExactSqrtWhiteBox(unittest.TestCase):
    def test_split_square(self):
        self.assertEqual(_split_square(72), (6, 2))
        self.assertEqual(_split_square(1), (1, 1))
        self.assertEqual(_split_square(49), (7, 1))

    def test_large_prime_cofactor_square(self):
        p = 10_007  # prime > trial limit
        self.assertEqual(_split_square(p * p * 3), (p, 3))

    def test_large_prime_cofactor_not_square(self):
        p, q = 10_007, 10_009
        self.assertEqual(_split_square(p * q), (1, p * q))

    def test_fraction_reduction(self):
        self.assertEqual(exact_sqrt_of_rational(Fraction(8, 9)), "2√2/3")
        self.assertEqual(exact_sqrt_of_rational(Fraction(-1, 3)), "i√3/3")


if __name__ == "__main__":
    unittest.main()
