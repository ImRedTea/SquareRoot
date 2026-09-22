"""Symbolic simplification for expressions that may contain `Variable` nodes.

sqrt(x^n) for a literal integer exponent n is reduced using the identities
sqrt(x^(2k)) = |x^k| and, for odd n = 2k+1, sqrt(x^(2k+1)) = |x^k| * sqrt(x)
(`|.|` is `Complex.modulus()`, reused via the existing `abs` function). Both
are exact for any REAL x regardless of sign: `sqrt(a^2)` simplifies to
`abs(a)`, not `a`, precisely so that `sqrt((-3)^2)` comes out to 3, not -3.

This still assumes the substituted value is real: for a variable later bound
to a genuinely complex (non-real) number, sqrt(x^2) is not generally equal
to |x| (there is no single algebraic correction factor for a complex base),
so results may not match the true principal square root in that case. This
is inherent to simplifying square roots symbolically without sign/branch
tracking on non-real values.

A separate, unresolved limitation: distributing sqrt over a PRODUCT OF TWO
DIFFERENT symbolic factors (`sqrt(a*b) -> sqrt(a)*sqrt(b)`) is not sound in
general once both factors can be negative/complex -- e.g. substituting
a=-4, b=-9 gives sqrt(a)*sqrt(b) = 2i*3i = -6, while the true sqrt(a*b) =
sqrt(36) = 6. This mirrors the classic complex-sqrt branch-cut pitfall
(sqrt(-1)*sqrt(-1) = -1, not sqrt((-1)*(-1)) = 1) and has no simple fix
without tracking arguments/branches through the whole expression tree. It
is a known, accepted limitation, distinct from (and not fixed by) the
abs() correction above -- which only concerns a single base raised to a
power, not a product of two independent symbolic radicands.

Two of the algebraic identities below (`x*0 -> 0`, `x^0 -> 1`) discard a
still-symbolic subtree. Both are verified zero-exception tautologies in
this codebase's arithmetic (`Complex._int_power(0)` never inspects `self`;
`Complex.__mul__` never raises), but the consequence is that
`evaluate(expr, variables=v)` is not always equivalent to "substitute v
into the unsimplified expr, then eagerly evaluate": e.g.
`evaluate("(1/a)*0", variables={"a": "0"})` returns 0 rather than raising
DivisionByZeroError, because `1/a` is discarded before `a` is bound. This
is standard simplify-then-substitute CAS behavior and is intentional.

By contrast `0/x -> 0` is deliberately NOT an identity here: unlike the
above, `Complex.__truediv__` raises DivisionByZeroError whenever the
denominator is zero regardless of the numerator, so `0/0` must still raise.
"""

from .complex_number import Complex
from .errors import DivisionByZeroError, UnknownFunctionError
from .parser import BinOp, Call, Literal, UnaryOp, Variable, _FUNCTIONS

PREC_SUM, PREC_PRODUCT, PREC_UNARY, PREC_POWER, PREC_ATOM = 1, 2, 3, 4, 5
_BIN_PREC = {"+": PREC_SUM, "-": PREC_SUM, "*": PREC_PRODUCT, "/": PREC_PRODUCT, "^": PREC_POWER}

_ZERO = Literal(Complex(0, 0))
_ONE = Literal(Complex(1, 0))


def simplify(node):
    if isinstance(node, Literal):
        return node
    if isinstance(node, Variable):
        return node
    if isinstance(node, UnaryOp):
        return _simplify_unary(node)
    if isinstance(node, BinOp):
        return _simplify_binop(node)
    if isinstance(node, Call):
        return _simplify_call(node)
    raise TypeError(f"unexpected node type {type(node)!r}")


def _simplify_unary(node):
    operand = simplify(node.operand)
    if node.op == "+":
        return operand
    if isinstance(operand, Literal):
        return Literal(-operand.value)
    return UnaryOp(node.op, operand)


def _simplify_binop(node):
    left = simplify(node.left)
    right = simplify(node.right)
    if isinstance(left, Literal) and isinstance(right, Literal):
        return Literal(_fold_binop(node.op, left.value, right.value))
    return _simplify_binop_identity(node.op, left, right)


def _fold_binop(op, left, right):
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        return left / right
    if op == "^":
        return left ** right
    raise ValueError(f"unknown operator {op!r}")


def _simplify_binop_identity(op, left, right):
    if op == "+":
        if left == _ZERO:
            return right
        if right == _ZERO:
            return left
    elif op == "-":
        if right == _ZERO:
            return left
        if left == _ZERO:
            return UnaryOp("-", right)
    elif op == "*":
        if left == _ONE:
            return right
        if right == _ONE:
            return left
        if left == _ZERO or right == _ZERO:
            return _ZERO
    elif op == "/":
        if right == _ONE:
            return left
        # Intentionally no `left == _ZERO -> _ZERO` rule here: 0/x is not a
        # tautology, since 0/0 must still raise DivisionByZeroError.
    elif op == "^":
        if isinstance(right, Literal) and _is_literal_integer(right.value) and right.value.real == 0:
            return _ONE
        if right == _ONE:
            return left
    return BinOp(op, left, right)


def _is_literal_integer(value):
    return value.imag == 0 and value.real == value.real.to_integral_value()


def _simplify_call(node):
    name = node.name.lower()
    if name not in _FUNCTIONS:
        raise UnknownFunctionError(f"unknown function {node.name!r}")
    arg = simplify(node.arg)
    if name == "sqrt":
        return _simplify_sqrt(arg)
    if isinstance(arg, Literal):
        return Literal(_FUNCTIONS[name](arg.value))
    return Call(node.name, arg)


def _simplify_sqrt(arg):
    if isinstance(arg, Literal):
        return Literal(arg.value.sqrt())
    if isinstance(arg, BinOp) and arg.op == "*":
        return simplify(BinOp("*", Call("sqrt", arg.left), Call("sqrt", arg.right)))
    if isinstance(arg, BinOp) and arg.op == "/":
        return simplify(BinOp("/", Call("sqrt", arg.left), Call("sqrt", arg.right)))
    if isinstance(arg, BinOp) and arg.op == "^":
        exponent = arg.right
        if isinstance(exponent, Literal) and _is_literal_integer(exponent.value):
            n = int(exponent.value.real)
            if n % 2 == 0:
                half_power = BinOp("^", arg.left, Literal(Complex(n // 2, 0)))
                return simplify(Call("abs", half_power))
            half_power = BinOp("^", arg.left, Literal(Complex((n - 1) // 2, 0)))
            return simplify(BinOp("*", Call("abs", half_power), Call("sqrt", arg.left)))
    return Call("sqrt", arg)


def substitute(node, bindings):
    if isinstance(node, Literal):
        return node
    if isinstance(node, Variable):
        return Literal(bindings[node.name]) if node.name in bindings else node
    if isinstance(node, UnaryOp):
        return UnaryOp(node.op, substitute(node.operand, bindings))
    if isinstance(node, BinOp):
        return BinOp(node.op, substitute(node.left, bindings), substitute(node.right, bindings))
    if isinstance(node, Call):
        return Call(node.name, substitute(node.arg, bindings))
    raise TypeError(f"unexpected node type {type(node)!r}")


def free_variables(node):
    if isinstance(node, Literal):
        return frozenset()
    if isinstance(node, Variable):
        return frozenset((node.name,))
    if isinstance(node, UnaryOp):
        return free_variables(node.operand)
    if isinstance(node, BinOp):
        return free_variables(node.left) | free_variables(node.right)
    if isinstance(node, Call):
        return free_variables(node.arg)
    raise TypeError(f"unexpected node type {type(node)!r}")


def render(node):
    text, _ = _render(node)
    return text


def _render(node):
    if isinstance(node, Literal):
        return _render_literal(node.value)
    if isinstance(node, Variable):
        return node.name, PREC_ATOM
    if isinstance(node, Call):
        return f"{node.name}({render(node.arg)})", PREC_ATOM
    if isinstance(node, UnaryOp):
        operand_text, operand_prec = _render(node.operand)
        if operand_prec < PREC_UNARY:
            operand_text = f"({operand_text})"
        return f"{node.op}{operand_text}", PREC_UNARY
    if isinstance(node, BinOp):
        return _render_binop(node)
    raise TypeError(f"unexpected node type {type(node)!r}")


def _render_binop(node):
    left_text, left_prec = _render(node.left)
    right_text, right_prec = _render(node.right)
    prec = _BIN_PREC[node.op]
    if node.op == "^":
        if left_prec <= prec:
            left_text = f"({left_text})"
        if right_prec < prec:
            right_text = f"({right_text})"
    else:
        if left_prec < prec:
            left_text = f"({left_text})"
        if right_prec <= prec:
            right_text = f"({right_text})"
    return f"{left_text}{node.op}{right_text}", prec


def _render_literal(value):
    text = str(value)
    if value.real != 0 and value.imag != 0:
        return text, PREC_SUM
    if text.startswith("-"):
        return text, PREC_UNARY
    return text, PREC_ATOM
