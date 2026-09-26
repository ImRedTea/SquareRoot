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
    exact: str = ""  # closed form such as "2√2"; "" when there is none


def compute(radicand, variables, precision, language=i18n.DEFAULT_LANGUAGE):
    """Always evaluates sqrt(<radicand>) -- wrapped exactly once, so a
    radicand that itself contains "sqrt(...)" is not double-unwrapped.
    """
    expression = f"sqrt({radicand})"
    try:
        result = squareroot.evaluate(expression, variables=variables, precision=precision)
        value = str(result)
    except SquareRootError as e:
        return _error_result(
            radicand,
            type(e).__name__,
            i18n.error_type_label(language, e),
            i18n.translate_error(language, e),
        )
    except Exception as e:
        # Last line of defence: an exception escaping into a Tk callback is
        # invisible to the user, so any bug must still surface as an error.
        return _error_result(
            radicand,
            "InternalError",
            i18n.translate(language, "error.internal.label"),
            i18n.translate(language, "error.internal.message", name=type(e).__name__),
        )

    if isinstance(result, Complex):
        exact = squareroot.exact_sqrt(radicand, variables) or ""
        return ComputeResult(
            state="numeric",
            header=f"√({radicand}) =",
            value=value,
            error_type="",
            error_type_label="",
            error_message="",
            hint="",
            exact=exact,
        )

    return ComputeResult(
        state="symbolic",
        header=f"√({radicand}){i18n.translate(language, 'header.symbolic_suffix')}",
        value=value,
        error_type="",
        error_type_label="",
        error_message="",
        hint=i18n.translate(language, "hint.provide_value"),
    )


def _error_result(radicand, error_type, label, message):
    return ComputeResult(
        state="error",
        header=f"√({radicand})",
        value="",
        error_type=error_type,
        error_type_label=label,
        error_message=message,
        hint="",
    )


@dataclass(frozen=True)
class UpdateMessage:
    kind: str  # "available" | "latest" | "error"
    title: str
    message: str
    url: str  # release page to open when kind == "available", else ""


def describe_update(check, language=i18n.DEFAULT_LANGUAGE):
    """Run `check()` (updates.check_for_update) and turn the outcome into a
    localized dialog text. Never raises: any failure is kind="error"."""
    title = i18n.translate(language, "dialog.update.title")
    try:
        info = check()
        newer = info.is_newer
    except Exception:
        return UpdateMessage("error", title, i18n.translate(language, "dialog.update.error"), "")
    if newer:
        text = i18n.translate(
            language, "dialog.update.available", latest=info.latest, current=info.current
        )
        return UpdateMessage("available", title, text, info.url)
    text = i18n.translate(language, "dialog.update.latest", current=info.current)
    return UpdateMessage("latest", title, text, "")
