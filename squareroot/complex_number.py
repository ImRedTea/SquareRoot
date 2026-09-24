from decimal import Decimal

from .errors import DivisionByZeroError, UnsupportedOperationError

_EQ_TOLERANCE = Decimal("1E-9")


def _to_decimal(value):
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        raise TypeError("cannot convert bool to Decimal")
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        return Decimal(value)
    if isinstance(value, float):
        raise TypeError(
            "Complex does not accept float values; use Decimal, int, or str"
        )
    raise TypeError(f"cannot convert {value!r} to Decimal")


class Complex:
    __slots__ = ("real", "imag")

    def __init__(self, real=0, imag=0):
        self.real = _to_decimal(real)
        self.imag = _to_decimal(imag)

    @classmethod
    def from_str(cls, s):
        s = s.strip()
        if not s:
            raise ValueError("cannot parse complex literal from empty string")

        if s[-1] in ("i", "I"):
            rest = s[1:]
            split_at = None
            for i in range(len(rest) - 1, -1, -1):
                if rest[i] in "+-":
                    split_at = i
                    break
            if split_at is None:
                real_str, imag_str = None, s
            else:
                real_str, imag_str = s[: split_at + 1], s[split_at + 1:]
        else:
            real_str, imag_str = s, None

        real = Decimal(real_str) if real_str else Decimal(0)

        if imag_str is None:
            imag = Decimal(0)
        else:
            coeff_str = imag_str[:-1]
            if coeff_str in ("", "+"):
                imag = Decimal(1)
            elif coeff_str == "-":
                imag = Decimal(-1)
            else:
                imag = Decimal(coeff_str)

        return cls(real, imag)

    def __add__(self, other):
        other = self._coerce(other)
        return Complex(self.real + other.real, self.imag + other.imag)

    __radd__ = __add__

    def __sub__(self, other):
        other = self._coerce(other)
        return Complex(self.real - other.real, self.imag - other.imag)

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        return Complex(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real,
        )

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self._coerce(other)
        denom = other.real * other.real + other.imag * other.imag
        if denom == 0:
            raise DivisionByZeroError("division by zero", code="division_by_zero")
        return Complex(
            (self.real * other.real + self.imag * other.imag) / denom,
            (self.imag * other.real - self.real * other.imag) / denom,
        )

    def __rtruediv__(self, other):
        return self._coerce(other) / self

    def __neg__(self):
        return Complex(-self.real, -self.imag)

    def __pos__(self):
        return Complex(self.real, self.imag)

    def __pow__(self, exponent):
        exponent = self._coerce(exponent)
        if exponent.imag == 0 and exponent.real == exponent.real.to_integral_value():
            return self._int_power(int(exponent.real))
        return self._real_power(exponent)

    def _int_power(self, n):
        if n == 0:
            return Complex(1, 0)
        base = self if n > 0 else Complex(1, 0) / self
        result = Complex(1, 0)
        for _ in range(abs(n)):
            result = result * base
        return result

    def _real_power(self, exponent):
        if self.imag != 0 or self.real < 0 or exponent.imag != 0:
            raise UnsupportedOperationError(
                "a non-integer power is only supported for a non-negative real "
                "base with a real exponent",
                code="non_integer_power_complex_base",
            )
        if self.real == 0:
            if exponent.real > 0:
                return Complex(0, 0)
            raise DivisionByZeroError(
                "0 cannot be raised to a non-positive power", code="zero_to_nonpositive_power"
            )
        magnitude = (exponent.real * self.real.ln()).exp()
        return Complex(magnitude, 0)

    def sqrt(self):
        if self.imag == 0:
            if self.real >= 0:
                return Complex(self.real.sqrt(), 0)
            return Complex(0, (-self.real).sqrt())
        modulus = self.modulus()
        x = ((modulus + self.real) / 2).sqrt()
        y = ((modulus - self.real) / 2).sqrt()
        if self.imag < 0:
            y = -y
        return Complex(x, y)

    def conjugate(self):
        return Complex(self.real, -self.imag)

    def modulus(self):
        return (self.real * self.real + self.imag * self.imag).sqrt()

    __abs__ = modulus

    def __eq__(self, other):
        if not isinstance(other, (Complex, int, str, Decimal)):
            return NotImplemented
        other = self._coerce(other)
        return (
            abs(self.real - other.real) <= _EQ_TOLERANCE
            and abs(self.imag - other.imag) <= _EQ_TOLERANCE
        )

    def __hash__(self):
        return hash((round(self.real, 9), round(self.imag, 9)))

    def __repr__(self):
        return f"Complex({self.real!r}, {self.imag!r})"

    def __str__(self):
        # sqrt()/pow() are computed to the active decimal precision, so a
        # mathematically-zero component can be left as tiny noise; snap it
        # for display only.
        real = Decimal(0) if abs(self.real) < _EQ_TOLERANCE else self.real
        imag = Decimal(0) if abs(self.imag) < _EQ_TOLERANCE else self.imag
        if imag == 0:
            return self._format_component(real)
        if real == 0:
            return self._format_imag_only(imag)
        sign = "+" if imag > 0 else "-"
        return f"{self._format_component(real)}{sign}{self._format_imag_only(abs(imag))}"

    def _format_imag_only(self, value):
        if value == 1:
            return "i"
        if value == -1:
            return "-i"
        return f"{self._format_component(value)}i"

    @staticmethod
    def _format_component(value):
        if value == 0:
            return "0"
        if value == value.to_integral_value():
            return str(value.to_integral_value())
        text = format(value, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text

    @staticmethod
    def _coerce(value):
        if isinstance(value, Complex):
            return value
        if isinstance(value, (int, str, Decimal)):
            return Complex(value, 0)
        raise TypeError(f"cannot coerce {value!r} to Complex")
