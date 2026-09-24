import re
from dataclasses import dataclass
from decimal import Decimal

from .complex_number import Complex
from .errors import ParseError, TokenizeError

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

    def parse(self):
        node = self._expression()
        self._expect("EOF")
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
        if self._peek().type in ("PLUS", "MINUS"):
            op = self._advance()
            return UnaryOp(op.value, self._unary())
        return self._power()

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


def parse(text):
    return Parser(tokenize(text)).parse()
