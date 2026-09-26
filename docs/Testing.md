# Testing

Run everything: `python -m unittest discover -s tests -t .`

| Layer | Method | Files |
|---|---|---|
| Unit (white box) | per-module tests written with the code in view | `test_complex_number.py`, `test_parser.py`, `test_simplify.py`, `test_api.py`, `test_ui_logic.py`, `test_i18n.py` |
| White box, coverage gaps | branches found by `coverage report` | `test_whitebox_gaps.py` |
| Black box, API | public `evaluate`/`Complex`/`Expression` only; equivalence classes + boundaries (precision 1/28/100, perfect squares, negatives, complex, variables, every error class); expected values from math | `test_blackbox_api.py` |
| Black box, GUI logic | `ui.logic.compute` as a user sees it, all 5 languages | `test_blackbox_gui_logic.py` |
| Black box, fault tolerance | hostile/extreme input must end in a `SquareRootError` within 5 s: overflow (`9^9^9^9`, `10^999999999`), huge integer powers (`1^100000000`, `i^(10^19+3)`), deep nesting / long chains, invalid precision (0, -1, 1001, 2.5, `True`), invalid variable values (`abc`, `nan`, `inf`, `1,5`) | `test_blackbox_api.py` (`FaultTolerance`), `test_blackbox_gui_logic.py` (`FaultTolerance`) |
| White box, safety nets | `RecursionError` past the explicit depth limits → `ExpressionTooComplexError`; any unexpected exception in the GUI logic → localized "Internal error" instead of a silent Tk callback failure | `test_whitebox_gaps.py`, `test_ui_logic.py` |
| Exact form (white + black box) | closed forms checked against known values and numerically against `evaluate` to 40 digits; unsupported input returns `None`, never raises | `test_exact.py`, `test_blackbox_gui_logic.py` (`ExactFormInGui`) |
| Update check (network mocked) | version parsing, newer/same/failed release lookups, localized dialog text in all languages | `test_updates.py` |
| Localisation | key parity across ru/en/es/zh/ja, every error code rendered, locale detection | `test_i18n.py` |

## Coverage

```
pip install coverage
coverage run -m unittest discover -s tests -t .
coverage report
```

Branch coverage, `squareroot/` package. `ui/app.py` (Tk widgets) is excluded;
its logic lives in `ui/logic.py` and `ui/i18n.py`, which are covered 100%.
CI fails below 95%.

| Date | Tests | Coverage |
|---|---|---|
| 2026-09-26 | 160 | 97% |
| 2026-09-26 (fault tolerance) | 177 | 98% |
| 2026-09-26 (exact form, updates) | 197 | 98% |

## Fault tolerance

Every failure a user or library caller can trigger is a `SquareRootError`
subclass with a machine-readable `code`, translated in all UI languages:

| Situation | Error | Code |
|---|---|---|
| Result or intermediate value exceeds the decimal range | `NumberOverflowError` | `overflow` |
| Nesting over 100 levels or expression tree deeper than 150 | `ExpressionTooComplexError` | `too_complex` |
| Precision not an integer in 1–1000 | `InvalidPrecisionError` | `invalid_precision` |
| Variable value not a finite real/complex number | `InvalidVariableValueError` | `invalid_variable_value` |
| Integer exponent longer than the precision on a base of modulus 1 (other than 1) | `UnsupportedOperationError` | `exponent_too_large` |

Integer powers use binary exponentiation (`log2(n)` multiplications), so
`1^100000000` answers instantly instead of looping for minutes.

The earlier known finding (`precision=0` raised a bare `ValueError`) is fixed:
it is now `InvalidPrecisionError`.
