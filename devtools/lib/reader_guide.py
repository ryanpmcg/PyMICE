"""Reader-facing copy shared across vignette reports."""

from __future__ import annotations

READER_DISCLAIMER = (
    "This walkthrough mirrors the official R **mice** tutorials in Python. "
    "Deterministic tables and formulas are checked against the R reference; "
    "stochastic imputations and plots are labelled when they may differ."
)

PYMICE_DIFFERENCES = """\
**What PyMICE does differently from R**

- Default randomness uses NumPy (`rng="numpy"`), so imputed values may differ from R unless you set `rng="r"`.
- Categorical factors are often shown as numeric codes in console output.
- Diagnostic figures use matplotlib instead of lattice (same intent, different styling).
- See [REPRODUCIBILITY.md](https://github.com/ryanpmcg/PyMICE/blob/main/docs/dev/REPRODUCIBILITY.md) for exact replication options.
"""

LEARNING_PATH = [
    ("01", "Ad Hoc MICE", "Start here — first imputation workflow"),
    ("02", "Convergence Pooling", "Convergence traces and pooling"),
    ("03", "Missingness Models", "Missingness patterns and models"),
    ("04", "Passive Imputation", "Passive imputation and post-processing"),
    ("05", "Multilevel Data", "Multilevel / clustered imputation"),
    ("06", "Sensitivity Analysis", "δ sensitivity and survival"),
    ("07", "Ampute Simulation", "Simulate missingness (appendix)"),
    ("08", "Parallel MICE", "Parallel imputation (appendix)"),
]

STATUS_LEGEND = {
    "match": "Console output matches the R reference.",
    "info": "Informational or PyMICE-only (no R snapshot to compare).",
    "partial": "Algorithm or plot differs in documented ways (often RNG or matplotlib).",
    "skip": "R-only section (e.g. wall-clock benchmarks).",
    "mismatch": "Output differs from the R reference — needs investigation.",
}
