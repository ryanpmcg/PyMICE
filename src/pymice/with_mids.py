"""Apply an analysis function to each imputed dataset."""

from __future__ import annotations

from collections.abc import Callable

from pymice.analysis.ols import lm
from pymice.complete import complete
from pymice.types import FitResult, ImputationFits, Mids, Mira


def with_mids(
    data: Mids,
    expr: Callable[[object], FitResult] | str | None = None,
    *,
    formula: str | None = None,
    family: str | None = None,
) -> ImputationFits:
    """Run a complete-data analysis on each imputation (R ``with.mids``)."""
    if formula is None and isinstance(expr, str):
        formula = expr

    analyses: list[FitResult] = []
    for i in range(1, data.m + 1):
        completed = complete(data, i)
        if formula is not None:
            if family is not None:
                from pymice.analysis.glm import glm

                analyses.append(glm(formula, completed, data.column_names, family=family))
            else:
                analyses.append(lm(formula, completed, data.column_names))
        elif expr is not None and callable(expr):
            analyses.append(expr(completed))
        else:
            raise ValueError("Provide formula='y ~ x' or a callable expr")

    call = formula if formula is not None else repr(expr)
    return Mira(m=data.m, analyses=analyses, call=call)


def with_imputations(
    data: Mids,
    *,
    formula: str,
    family: str | None = None,
    expr: Callable[[object], FitResult] | None = None,
) -> ImputationFits:
    """Pythonic alias for ``with_mids`` with formula-first API."""
    return with_mids(data, expr=expr, formula=formula, family=family)
