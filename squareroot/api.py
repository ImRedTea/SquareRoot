import decimal

from .expression import Expression, _coerce_variable
from .parser import Literal, parse
from .simplify import simplify, substitute

DEFAULT_PRECISION = 28


def evaluate(expression, variables=None, precision=None):
    prec = DEFAULT_PRECISION if precision is None else precision
    with decimal.localcontext() as ctx:
        ctx.prec = prec
        node = simplify(parse(expression))
        if variables:
            bindings = {name: _coerce_variable(value) for name, value in variables.items()}
            node = simplify(substitute(node, bindings))
        return node.value if isinstance(node, Literal) else Expression(node)
