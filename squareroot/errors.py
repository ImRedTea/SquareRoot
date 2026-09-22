class SquareRootError(Exception):
    """Base class for all errors raised by the squareroot core."""


class TokenizeError(SquareRootError):
    """Raised when the tokenizer encounters an invalid character."""


class ParseError(SquareRootError):
    """Raised when the token stream does not match the expression grammar."""


class EvaluationError(SquareRootError):
    """Base class for errors raised while evaluating a parsed expression."""


class DivisionByZeroError(EvaluationError):
    """Raised when dividing by zero."""


class UnknownFunctionError(EvaluationError):
    """Raised when calling a function that is not defined."""


class UnsupportedOperationError(EvaluationError):
    """Raised for an operation this core does not (yet) support."""
