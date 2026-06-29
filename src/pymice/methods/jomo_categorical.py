"""Single-level categorical joint imputation (jomo1cat-style)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept
from pymice.methods.polyreg import _fit_multinomial, _predict_multinomial
from pymice.types import VariableSpec


def _encode_categories(
    values: NDArray[np.float64],
    spec: VariableSpec,
) -> tuple[NDArray[np.float64], list[float]]:
    """Map column to 0..K-1 codes; return levels for decoding."""
    levels = list(spec.levels) if spec.levels else sorted(np.unique(values[np.isfinite(values)]))
    code_map = {float(lv): i for i, lv in enumerate(levels)}
    out = np.full(values.shape, np.nan, dtype=np.float64)
    for i, val in enumerate(values):
        if np.isfinite(val):
            out[i] = code_map.get(float(val), 0)
    return out, levels


def _decode_categories(codes: NDArray[np.float64], levels: list[float]) -> NDArray[np.float64]:
    idx = np.clip(np.rint(codes), 0, len(levels) - 1).astype(int)
    return np.array([levels[i] for i in idx], dtype=np.float64)


def _cat_dummies(codes: NDArray[np.float64], n_classes: int) -> NDArray[np.float64]:
    n = codes.shape[0]
    dummies = np.zeros((n, max(n_classes - 1, 0)), dtype=np.float64)
    for j in range(1, n_classes):
        dummies[:, j - 1] = (codes == j).astype(np.float64)
    return dummies


def jomo1cat_impute(
    y_cat: NDArray[np.float64],
    specs: list[VariableSpec],
    x: NDArray[np.float64] | None = None,
    *,
    n_burn: int = 100,
    n_iter: int = 10,
    rng: np.random.Generator,
) -> NDArray[np.float64]:
    """Latent-probit / multinomial Gibbs for categorical targets (jomo1cat approximation)."""
    n, k = y_cat.shape
    if x is None:
        x = np.ones((n, 1), dtype=np.float64)
    x_full = add_intercept(np.asarray(x, dtype=np.float64))

    work = y_cat.copy()
    level_lists: list[list[float]] = []
    n_classes: list[int] = []
    for j in range(k):
        codes, levels = _encode_categories(work[:, j], specs[j])
        work[:, j] = codes
        level_lists.append(levels)
        n_classes.append(len(levels))

    total = max(int(n_burn), 0) + max(int(n_iter), 1)
    for _ in range(total):
        for j in range(k):
            yj = work[:, j]
            mask = np.isfinite(yj)
            if int(np.sum(mask)) < 2:
                continue
            other = [c for c in range(k) if c != j]
            x_aug = x_full
            if other:
                parts = [_cat_dummies(work[:, c], n_classes[c]) for c in other]
                x_aug = np.column_stack([x_full, *parts])

            y_codes = yj[mask].astype(int)
            weights = np.ones(int(np.sum(mask)), dtype=np.float64)
            beta = _fit_multinomial(x_aug[mask], y_codes, weights, n_classes[j])
            miss = ~np.isfinite(yj)
            if np.any(miss):
                probs = _predict_multinomial(x_aug[miss], beta, n_classes[j])
                draws = np.array(
                    [rng.choice(n_classes[j], p=probs[i]) for i in range(probs.shape[0])],
                    dtype=np.float64,
                )
                work[miss, j] = draws

    out = np.empty_like(y_cat)
    for j in range(k):
        filled = work[:, j].copy()
        miss = ~np.isfinite(filled)
        if np.any(miss):
            obs_codes = work[np.isfinite(work[:, j]), j]
            if obs_codes.size:
                filled[miss] = rng.choice(obs_codes, size=int(np.sum(miss)))
        out[:, j] = _decode_categories(filled, level_lists[j])
    return out
