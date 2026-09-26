"""Exact (closed-form) square roots of rational radicands.

`evaluate("sqrt(8)")` returns a decimal approximation; `exact_sqrt("8")`
returns the closed form "2√2". Works for any radicand that reduces to a
REAL RATIONAL number using + - * / ^(integer) and parentheses, e.g.
"8", "-12", "1/2", "0.75", "2^5/3". Anything else (imaginary literals,
functions, unbound variables, huge numbers) returns None -- the caller then
simply shows no exact form. It never raises.

Result is always mathematically exact. The square factor is extracted by
trial division up to _TRIAL_LIMIT; for radicands with a large repeated prime
factor the form may be not fully reduced (e.g. 2√(p²·3)), but still correct.
"""

from decimal import Decimal
from fractions import Fraction
from math import gcd, isqrt

from .errors import SquareRootError
from .parser import BinOp, Call, Literal, UnaryOp, Variable, parse

_MAX_DIGITS = 60  # numerator/denominator size guard (digits)
_MAX_EXPONENT = 256
_TRIAL_LIMIT = 10_000


class _NotRational(Exception):
    pass


def _check_size(value):
    limit = 10**_MAX_DIGITS
    if abs(value.numerator) >= limit or value.denominator >= limit:
        raise _NotRational
    return value


def _to_fraction(text):
    try:
        number = Decimal(str(text).strip())
    except Exception:
        raise _NotRational from None
    if not number.is_finite():
        raise _NotRational
    return _check_size(Fraction(number))


def _rational(node, bindings):
    if isinstance(node, Literal):
        if node.value.imag != 0:
            raise _NotRational
        return _check_size(Fraction(node.value.real))
    if isinstance(node, Variable):
        if node.name not in bindings:
            raise _NotRational
        return _to_fraction(bindings[node.name])
    if isinstance(node, UnaryOp):
        value = _rational(node.operand, bindings)
        return -value if node.op == "-" else value
    if isinstance(node, BinOp):
        left = _rational(node.left, bindings)
        right = _rational(node.right, bindings)
        if node.op == "+":
            return _check_size(left + right)
        if node.op == "-":
            return _check_size(left - right)
        if node.op == "*":
            return _check_size(left * right)
        if node.op == "/":
            if right == 0:
                raise _NotRational
            return _check_size(left / right)
        if node.op == "^":
            if right.denominator != 1 or abs(right.numerator) > _MAX_EXPONENT:
                raise _NotRational
            if left == 0 and right.numerator <= 0:
                raise _NotRational
            return _check_size(left**right.numerator)
    if isinstance(node, Call):
        raise _NotRational
    raise _NotRational


def _split_square(n):
    """n > 0 -> (a, b) with n == a*a*b; b has no square factor <= _TRIAL_LIMIT."""
    a, b = 1, 1
    d = 2
    while d <= _TRIAL_LIMIT and d * d <= n:
        while n % (d * d) == 0:
            n //= d * d
            a *= d
        if n % d == 0:
            n //= d
            b *= d
        d += 1
    root = isqrt(n)
    if root * root == n:
        a *= root
    else:
        b *= n
    return a, b


def exact_sqrt_of_rational(value):
    """Closed form of sqrt(value) for a Fraction, or None if it is rational."""
    value = Fraction(value)
    if value == 0:
        return None
    negative = value < 0
    p, q = abs(value.numerator), value.denominator
    # sqrt(p/q) = sqrt(p*q) / q
    a, b = _split_square(p * q)
    if b == 1:
        return None  # the root is rational: the decimal result is already exact
    g = gcd(a, q)
    a, q = a // g, q // g
    text = ("" if a == 1 else str(a)) + ("i" if negative else "") + f"√{b}"
    if q != 1:
        text += f"/{q}"
    return text


def exact_sqrt(expression, variables=None):
    """Closed form of sqrt(<expression>) as a string, or None (never raises)."""
    try:
        node = parse(expression)
        value = _rational(node, dict(variables or {}))
        return exact_sqrt_of_rational(value)
    except (_NotRational, SquareRootError, RecursionError, ValueError, ArithmeticError):
        return None
