from dataclasses import dataclass

from .complex_number import Complex
from .parser import Literal
from .simplify import free_variables, render, simplify, substitute


def _coerce_variable(value):
    return Complex._coerce(value)


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
        bindings = {name: _coerce_variable(value) for name, value in variables.items()}
        new_node = simplify(substitute(self.node, bindings))
        return new_node.value if isinstance(new_node, Literal) else Expression(new_node)
