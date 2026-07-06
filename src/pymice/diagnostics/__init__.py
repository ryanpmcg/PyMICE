"""Diagnostic utilities for missing-data inspection."""

from pymice.diagnostics.convergence import ConvergenceRow, convergence
from pymice.diagnostics.flux import FluxResult, flux
from pymice.diagnostics.md_pattern import MdPatternResult, md_pattern
from pymice.diagnostics.theme import (
    COLOR_COMBINED,
    COLOR_COMBINED_LINE,
    COLOR_MISSING,
    COLOR_MISSING_LINE,
    COLOR_OBSERVED,
    COLOR_OBSERVED_LINE,
    mdc,
)

__all__ = [
    "COLOR_COMBINED",
    "COLOR_COMBINED_LINE",
    "COLOR_MISSING",
    "COLOR_MISSING_LINE",
    "COLOR_OBSERVED",
    "COLOR_OBSERVED_LINE",
    "ConvergenceRow",
    "FluxResult",
    "MdPatternResult",
    "convergence",
    "flux",
    "md_pattern",
    "mdc",
]

# Optional plots (requires [plot]):
# ``from pymice import plot, densityplot, stripplot, xyplot, bwplot``
# or ``from pymice.diagnostics.plots import plot_mids, ...``
