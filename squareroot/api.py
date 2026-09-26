import decimal

from .errors import InvalidPrecisionError
from .expression import Expression, _bind, _guard_runtime_errors
from .parser import Literal, parse
from .simplify import simplify, substitute

DEFAULT_PRECISION = 28
MIN_PRECISION = 1
MAX_PRECISION = 1000


def evaluate(expression, variables=None, precision=None):
    prec = DEFAULT_PRECISION if precision is None else precision
    if (
        isinstance(prec, bool)
        or not isinstance(prec, int)
        or not MIN_PRECISION <= prec <= MAX_PRECISION
    ):
        raise InvalidPrecisionError(
            f"precision must be an integer from {MIN_PRECISION} to {MAX_PRECISION}, got {prec!r}",
            code="invalid_precision",
            min=MIN_PRECISION,
            max=MAX_PRECISION,
        )
    bindings = _bind(variables) if variables else None
    with decimal.localcontext() as ctx, _guard_runtime_errors():
        ctx.prec = prec
        node = simplify(parse(expression))
        if bindings:
            node = simplify(substitute(node, bindings))
        return node.value if isinstance(node, Literal) else Expression(node)
