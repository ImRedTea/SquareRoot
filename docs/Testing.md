# Testing

Run everything: `python -m unittest discover -s tests -t .`

| Layer | Method | Files |
|---|---|---|
| Unit (white box) | per-module tests written with the code in view | `test_complex_number.py`, `test_parser.py`, `test_simplify.py`, `test_api.py`, `test_ui_logic.py`, `test_i18n.py` |
| White box, coverage gaps | branches found by `coverage report` | `test_whitebox_gaps.py` |
| Black box, API | public `evaluate`/`Complex`/`Expression` only; equivalence classes + boundaries (precision 1/28/100, perfect squares, negatives, complex, variables, every error class); expected values from math | `test_blackbox_api.py` |
| Black box, GUI logic | `ui.logic.compute` as a user sees it, all 5 languages | `test_blackbox_gui_logic.py` |
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

## Known finding

`evaluate(..., precision=0 or negative)` raises a bare `ValueError` from
`decimal`, not a `SquareRootError`. The GUI validates the range (1–100) before
calling the API, so users can't hit it; a library caller can.
