"""Alias for multilevel-binary setup (R vignette comment ``#2logreg``)."""

from __future__ import annotations

from pymice.methods.logreg import impute_logreg
from pymice.methods.registry import register_method

# R mice V05 uses method ``logreg`` for ``sex``; the ``#2logreg`` comment refers to
# predictor-matrix typing, not a separate imputation function. Register the alias so
# user code that names ``2logreg`` still runs.
register_method("2logreg", impute_logreg)
