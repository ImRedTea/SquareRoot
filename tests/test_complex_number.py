import unittest
from decimal import Decimal

from squareroot.complex_number import Complex
from squareroot.errors import DivisionByZeroError, UnsupportedOperationError


class ComplexArithmeticTests(unittest.TestCase):
    def test_rejects_float(self):
        with self.assertRaises(TypeError):
            Complex(1.5, 0)

    def test_addition(self):
        self.assertEqual(Complex(1, 2) + Complex(3, -1), Complex(4, 1))

    def test_subtraction(self):
        self.assertEqual(Complex(1, 2) - Complex(3, -1), Complex(-2, 3))

    def test_multiplication(self):
        self.assertEqual(Complex(1, 2) * Complex(3, 4), Complex(-5, 10))

    def test_division(self):
        result = Complex(1, 2) / Complex(3, 4)
        self.assertEqual(result, Complex(Decimal("0.44"), Decimal("0.08")))

    def test_division_by_zero_raises(self):
        with self.assertRaises(DivisionByZeroError):
            Complex(1, 1) / Complex(0, 0)

    def test_conjugate(self):
        self.assertEqual(Complex(3, -4).conjugate(), Complex(3, 4))

    def test_modulus(self):
        self.assertEqual(Complex(3, 4).modulus(), Decimal(5))

    def test_sqrt_negative_real(self):
        self.assertEqual(Complex(-4, 0).sqrt(), Complex(0, 2))

    def test_sqrt_zero(self):
        self.assertEqual(Complex(0, 0).sqrt(), Complex(0, 0))

    def test_sqrt_general_complex(self):
        result = Complex(3, 4).sqrt()
        self.assertEqual(result * result, Complex(3, 4))

    def test_integer_power(self):
        self.assertEqual(Complex(1, 1) ** 2, Complex(0, 2))

    def test_negative_integer_power(self):
        self.assertEqual(Complex(0, 1) ** -1, Complex(0, -1))

    def test_real_non_integer_power(self):
        self.assertEqual(Complex(4, 0) ** Complex(Decimal("0.5"), 0), Complex(2, 0))

    def test_non_integer_power_on_complex_base_raises(self):
        with self.assertRaises(UnsupportedOperationError):
            Complex(1, 1) ** Complex(Decimal("0.5"), 0)

    def test_from_str_forms(self):
        cases = {
            "5": Complex(5, 0),
            "-5": Complex(-5, 0),
            "3+4i": Complex(3, 4),
            "3-4i": Complex(3, -4),
            "-3-4i": Complex(-3, -4),
            "4i": Complex(0, 4),
            "-4i": Complex(0, -4),
            "i": Complex(0, 1),
            "-i": Complex(0, -1),
        }
        for literal, expected in cases.items():
            with self.subTest(literal=literal):
                self.assertEqual(Complex.from_str(literal), expected)

    def test_str_formatting(self):
        self.assertEqual(str(Complex(3, 4)), "3+4i")
        self.assertEqual(str(Complex(3, -4)), "3-4i")
        self.assertEqual(str(Complex(3, 1)), "3+i")
        self.assertEqual(str(Complex(3, -1)), "3-i")
        self.assertEqual(str(Complex(0, 1)), "i")
        self.assertEqual(str(Complex(0, -1)), "-i")
        self.assertEqual(str(Complex(5, 0)), "5")
        self.assertEqual(str(Complex(0, 0)), "0")


if __name__ == "__main__":
    unittest.main()
