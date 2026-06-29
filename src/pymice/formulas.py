"""Regression and passive formula parsing (Python-native transforms)."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

_TRANSFORM_RE = re.compile(r"^(log10|log|sqrt)\((\w+)\)$")


@dataclass(frozen=True)
class PredictorTerm:
    """One design-matrix column with a display label."""

    label: str
    source: str
    transform: Callable[[NDArray[np.float64]], NDArray[np.float64]] | None = None


def _transform_fn(name: str) -> Callable[[NDArray[np.float64]], NDArray[np.float64]]:
    if name == "log10":
        return lambda x: np.log10(np.maximum(x, 1e-300))
    if name == "log":
        return lambda x: np.log(np.maximum(x, 1e-300))
    if name == "sqrt":
        return np.sqrt
    raise ValueError(f"unknown transform: {name}")


def parse_predictor(token: str, column_names: list[str]) -> PredictorTerm:
    """Parse one RHS token (``bw``, ``log10(bw)``, ``sqrt(x)``)."""
    token = token.strip()
    match = _TRANSFORM_RE.match(token)
    if match:
        fn_name, col = match.group(1), match.group(2)
        if col not in column_names:
            raise ValueError(f"Unknown variable in transform: {col}")
        return PredictorTerm(label=token, source=col, transform=_transform_fn(fn_name))
    if token not in column_names:
        raise ValueError(f"Unknown predictor: {token}")
    return PredictorTerm(label=token, source=token, transform=None)


def parse_regression_formula(
    formula: str,
    column_names: list[str],
) -> tuple[str, list[PredictorTerm]]:
    """Parse ``y ~ x1 + log10(x2)`` into response and predictor terms."""
    if "~" not in formula:
        raise ValueError("Formula must contain '~'")
    lhs, rhs = formula.split("~", 1)
    y_name = lhs.strip()
    if y_name not in column_names:
        raise ValueError(f"Unknown response variable: {y_name}")
    rhs = rhs.strip()
    if rhs == "1":
        return y_name, []
    tokens = [p.strip() for p in re.split(r"\s*\+\s*", rhs) if p.strip()]
    return y_name, [parse_predictor(t, column_names) for t in tokens]


def build_design_matrix(
    data: NDArray[np.float64],
    column_names: list[str],
    terms: list[PredictorTerm],
) -> NDArray[np.float64]:
    """Build OLS design matrix with intercept and transformed predictors."""
    cols = [np.ones(data.shape[0], dtype=np.float64)]
    for term in terms:
        col = data[:, column_names.index(term.source)]
        if term.transform is not None:
            col = term.transform(col)
        cols.append(col)
    return np.column_stack(cols) if len(cols) > 1 else cols[0].reshape(-1, 1)


def term_labels(terms: list[PredictorTerm]) -> list[str]:
    return ["(Intercept)"] + [t.label for t in terms]
