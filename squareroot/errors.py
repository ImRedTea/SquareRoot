class SquareRootError(Exception):
    """Base class for all errors raised by the squareroot core.

    Carries an optional machine-readable `code` and `params` alongside the
    English `message`, so callers (e.g. the UI) can re-render the error in
    another language without parsing `str(exc)`.
    """

    def __init__(self, message, *, code=None, **params):
        super().__init__(message)
        self.code = code or type(self).__name__
        self.params = params


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
