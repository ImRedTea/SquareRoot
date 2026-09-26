import re
from dataclasses import dataclass
from decimal import Decimal

from .complex_number import Complex
from .errors import ExpressionTooComplexError, ParseError, TokenizeError

# Parser, simplifier and renderer are recursive; these limits keep them well
# inside Python's default recursion limit (1000 frames) even when called from
# a GUI callback. Each nesting level costs ~5 parser frames; a symbolic
# product chain overflows the simplifier at ~200 tree levels.
MAX_NESTING = 100
MAX_TREE_DEPTH = 150

_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
_IDENT_RE = re.compile(r"[A-Za-z]+")

_SIMPLE_TOKENS = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
    "^": "CARET",
    "(": "LPAREN",
    ")": "RPAREN",
}

_FUNCTIONS = {
    "sqrt": lambda z: z.sqrt(),
    "conj": lambda z: z.conjugate(),
    "abs": lambda z: Complex(z.modulus(), 0),
    "re": lambda z: Complex(z.real, 0),
    "im": lambda z: Complex(z.imag, 0),
}


@dataclass(frozen=True)
class Token:
    type: str
    value: object
    pos: int


def tokenize(text):
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit() or ch == ".":
            match = _NUMBER_RE.match(text, i)
            if not match:
                raise TokenizeError(
                    f"invalid number at position {i}", code="invalid_number", position=i
                )
            literal = match.group()
            end = match.end()
            if end < n and text[end] in ("i", "I") and not (
                end + 1 < n and text[end + 1].isalpha()
            ):
                tokens.append(Token("IMAG", Decimal(literal), i))
                i = end + 1
            else:
                tokens.append(Token("NUMBER", Decimal(literal), i))
                i = end
            continue
        if ch.isalpha():
            match = _IDENT_RE.match(text, i)
            name = match.group()
            end = match.end()
            if name.lower() == "i":
                tokens.append(Token("IMAG", Decimal(1), i))
            else:
                tokens.append(Token("IDENT", name, i))
            i = end
            continue
        if ch in _SIMPLE_TOKENS:
            tokens.append(Token(_SIMPLE_TOKENS[ch], ch, i))
            i += 1
            continue
        raise TokenizeError(
            f"unexpected character {ch!r} at position {i}",
            code="unexpected_character",
            char=ch,
            position=i,
        )
    tokens.append(Token("EOF", None, n))
    return tokens


@dataclass
class Literal:
    value: Complex


@dataclass(frozen=True)
class Variable:
    # Matched verbatim (case-sensitive) against `variables` dict keys passed
    # to evaluate() -- unlike function names, which are matched case-insensitively.
    name: str


@dataclass
class UnaryOp:
    op: str
    operand: "Node"


@dataclass
class BinOp:
    op: str
    left: "Node"
    right: "Node"


@dataclass
class Call:
    name: str
    arg: "Node"


class Parser:
    def __init__(self, tokens):
        self._tokens = tokens
        self._pos = 0
        self._nesting = 0

    def parse(self):
        node = self._expression()
        self._expect("EOF")
        if _tree_depth(node) > MAX_TREE_DEPTH:
            raise _too_complex()
        return node

    def _peek(self):
        return self._tokens[self._pos]

    def _advance(self):
        token = self._tokens[self._pos]
        self._pos += 1
        return token

    def _expect(self, type_):
        token = self._peek()
        if token.type != type_:
            raise ParseError(
                f"expected {type_} but found {token.type} at position {token.pos}",
                code="expected_token",
                expected=type_,
                found=token.type,
                position=token.pos,
            )
        return self._advance()

    def _expression(self):
        node = self._term()
        while self._peek().type in ("PLUS", "MINUS"):
            op = self._advance()
            node = BinOp(op.value, node, self._term())
        return node

    def _term(self):
        node = self._unary()
        while self._peek().type in ("STAR", "SLASH"):
            op = self._advance()
            node = BinOp(op.value, node, self._unary())
        return node

    def _unary(self):
        # Every recursive path (parentheses, calls, unary signs, ^) passes here.
        self._nesting += 1
        if self._nesting > MAX_NESTING:
            raise _too_complex()
        try:
            if self._peek().type in ("PLUS", "MINUS"):
                op = self._advance()
                return UnaryOp(op.value, self._unary())
            return self._power()
        finally:
            self._nesting -= 1

    def _power(self):
        node = self._primary()
        if self._peek().type == "CARET":
            self._advance()
            exponent = self._unary()
            node = BinOp("^", node, exponent)
        return node

    def _primary(self):
        token = self._peek()
        if token.type == "NUMBER":
            self._advance()
            return Literal(Complex(token.value, 0))
        if token.type == "IMAG":
            self._advance()
            return Literal(Complex(0, token.value))
        if token.type == "IDENT":
            self._advance()
            if self._peek().type == "LPAREN":
                self._advance()
                arg = self._expression()
                self._expect("RPAREN")
                return Call(token.value, arg)
            return Variable(token.value)
        if token.type == "LPAREN":
            self._advance()
            node = self._expression()
            self._expect("RPAREN")
            return node
        raise ParseError(
            f"unexpected token {token.type} at position {token.pos}",
            code="unexpected_token",
            found=token.type,
            position=token.pos,
        )


def _too_complex():
    return ExpressionTooComplexError(
        f"expression is too complex (nesting over {MAX_NESTING} "
        f"or tree depth over {MAX_TREE_DEPTH})",
        code="too_complex",
    )


def _tree_depth(root):
    deepest = 0
    stack = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        deepest = max(deepest, depth)
        if isinstance(node, UnaryOp):
            stack.append((node.operand, depth + 1))
        elif isinstance(node, BinOp):
            stack.append((node.left, depth + 1))
            stack.append((node.right, depth + 1))
        elif isinstance(node, Call):
            stack.append((node.arg, depth + 1))
    return deepest


def parse(text):
    return Parser(tokenize(text)).parse()
