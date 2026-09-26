import decimal
from contextlib import contextmanager
from dataclasses import dataclass

from .complex_number import Complex
from .errors import ExpressionTooComplexError, InvalidVariableValueError, NumberOverflowError
from .parser import Literal
from .simplify import free_variables, render, simplify, substitute


def _coerce_variable(name, value):
    try:
        number = Complex.from_str(value) if isinstance(value, str) else Complex._coerce(value)
    except (ValueError, decimal.InvalidOperation):
        number = None
    if number is None or not (number.real.is_finite() and number.imag.is_finite()):
        raise InvalidVariableValueError(
            f"value of variable {name!r} is not a finite number: {value!r}",
            code="invalid_variable_value",
            name=name,
            value=str(value),
        )
    return number


@contextmanager
def _guard_runtime_errors():
    """Turn decimal overflow and runaway recursion into SquareRootErrors."""
    try:
        yield
    except decimal.Overflow:
        raise NumberOverflowError("result is too large to represent", code="overflow") from None
    except RecursionError:
        raise ExpressionTooComplexError("expression is too complex", code="too_complex") from None


def _bind(variables):
    return {name: _coerce_variable(name, value) for name, value in variables.items()}


@dataclass(frozen=True)
class Expression:
    node: object

    def __str__(self):
        return render(self.node)

    def __repr__(self):
        return f"Expression({str(self)!r})"

    def __eq__(self, other):
        if not isinstance(other, Expression):
            return NotImplemented
        return self.node == other.node

    def __hash__(self):
        return hash(render(self.node))

    @property
    def variables(self):
        return free_variables(self.node)

    def substitute(self, variables):
        bindings = _bind(variables)
        with _guard_runtime_errors():
            new_node = simplify(substitute(self.node, bindings))
        return new_node.value if isinstance(new_node, Literal) else Expression(new_node)
