"""Pure application logic for the SquareRoot GUI.

No `tkinter` import anywhere in this module -- it must stay importable and
unit-testable on systems where Tk is not installed.
"""

from dataclasses import dataclass

import squareroot
from squareroot import Complex
from squareroot.errors import SquareRootError
from squareroot.ui import i18n


def build_variables(raw_rows):
    """raw_rows: iterable of (name, value) str pairs as typed by the user.

    Rows with a blank name or blank value are skipped -- Decimal("") raises,
    so a blank must never reach evaluate(). Names/values are stripped; a
    later duplicate name overwrites an earlier one.
    """
    variables = {}
    for name, value in raw_rows:
        name = name.strip()
        value = value.strip()
        if not name or not value:
            continue
        variables[name] = value
    return variables


@dataclass(frozen=True)
class ComputeResult:
    state: str  # "numeric" | "symbolic" | "error"
    header: str
    value: str
    error_type: str  # stable, untranslated exception class name
    error_type_label: str  # localized display label for error_type
    error_message: str
    hint: str


def compute(radicand, variables, precision, language=i18n.DEFAULT_LANGUAGE):
    """Always evaluates sqrt(<radicand>) -- wrapped exactly once, so a
    radicand that itself contains "sqrt(...)" is not double-unwrapped.
    """
    expression = f"sqrt({radicand})"
    try:
        result = squareroot.evaluate(expression, variables=variables, precision=precision)
    except SquareRootError as e:
        return ComputeResult(
            state="error",
            header=f"√({radicand})",
            value="",
            error_type=type(e).__name__,
            error_type_label=i18n.error_type_label(language, e),
            error_message=i18n.translate_error(language, e),
            hint="",
        )

    if isinstance(result, Complex):
        return ComputeResult(
            state="numeric",
            header=f"√({radicand}) =",
            value=str(result),
            error_type="",
            error_type_label="",
            error_message="",
            hint="",
        )

    return ComputeResult(
        state="symbolic",
        header=f"√({radicand}){i18n.translate(language, 'header.symbolic_suffix')}",
        value=str(result),
        error_type="",
        error_type_label="",
        error_message="",
        hint=i18n.translate(language, "hint.provide_value"),
    )
