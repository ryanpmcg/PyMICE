"""Generate missing values for simulation (R ``ampute``)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class AmputeResult:
    """Amputed dataset and metadata (R ``mads`` subset)."""

    amp: NDArray[np.floating] | None
    patterns: NDArray[np.int_]
    freq: NDArray[np.floating]
    mech: str
    prop: float
    bycases: bool
    weights: NDArray[np.float64] | None = None
    scores: list[NDArray[np.float64]] | None = None
    cand: NDArray[np.int_] | None = None
    type_: list[str] | None = None
    cont: bool = True
    data: NDArray[np.float64] | None = None


def _default_patterns(n_cols: int) -> NDArray[np.int_]:
    pat = np.zeros((n_cols, n_cols), dtype=np.int_)
    for j in range(n_cols):
        pat[j, j] = 1
    return pat


def _default_freq(n_pat: int) -> NDArray[np.float64]:
    return np.full(n_pat, 1.0 / n_pat, dtype=np.float64)


def _default_weights(patterns: NDArray[np.int_], mech: str) -> NDArray[np.float64]:
    """R ``ampute.default.weights``."""
    n_pat, n_var = patterns.shape
    weights = np.ones((n_pat, n_var), dtype=np.float64)
    for i in range(n_pat):
        amputed = patterns[i] == 0
        if mech.upper() == "MAR":
            weights[i, amputed] = 0.0
        elif mech.upper() == "MNAR":
            weights[i, ~amputed] = 0.0
    return weights


def _default_type(n_pat: int) -> list[str]:
    return ["RIGHT"] * n_pat


def _recalculate_prop_cellwise(
    prop: float,
    freq: NDArray[np.float64],
    patterns: NDArray[np.int_],
    n_rows: int,
    n_cols: int,
) -> float:
    """Adjust ``prop`` when ``bycases=False`` (R ``recalculate.prop`` approximation)."""
    miss_per_pat = np.sum(patterns == 0, axis=1)
    expected_cells = float(n_rows * n_cols) * prop
    expected_cases = expected_cells / max(float(np.mean(miss_per_pat)), 1.0)
    return min(max(expected_cases / n_rows, 0.0), 1.0)


def _ampute_mcar(
    p: NDArray[np.int_],
    patterns: NDArray[np.int_],
    prop: float,
    rng: np.random.Generator,
) -> list[NDArray[np.int_]]:
    n_pat = patterns.shape[0]
    out: list[NDArray[np.int_]] = []
    for i in range(n_pat):
        code = i + 2
        mask = p == code
        if not np.any(mask):
            out.append(np.zeros_like(p, dtype=np.int_))
            continue
        r_temp = p.copy()
        n_cand = int(np.sum(mask))
        draws = 1 - rng.binomial(1, prop, size=n_cand)
        r_temp[mask] = draws
        r_temp[~mask] = 1
        out.append(r_temp)
    return out


def _logit(x: NDArray[np.float64]) -> NDArray[np.float64]:
    return np.exp(x) / (1.0 + np.exp(x))


def _bin_search(target: float, fn) -> float:
    lo, hi = -8.0, 8.0
    for _ in range(100):
        if hi - lo <= 1e-3:
            break
        center = (hi + lo) / 2.0
        val = fn(center)
        if val < target:
            lo = center
        else:
            hi = center
    return (lo + hi) / 2.0


def _ampute_continuous(
    p: NDArray[np.int_],
    scores: list[NDArray[np.float64]],
    prop: float,
    types: list[str],
    rng: np.random.Generator,
) -> list[NDArray[np.int_]]:
    testset = (rng.standard_normal(10_000)).astype(np.float64)
    testset = (testset - np.mean(testset)) / np.std(testset)

    out: list[NDArray[np.int_]] = []
    for i, score_vec in enumerate(scores):
        code = i + 2
        if score_vec.size == 1 and score_vec[0] == 0:
            out.append(np.zeros_like(p, dtype=np.int_))
            continue

        kind = types[i] if i < len(types) else "RIGHT"

        def _formula(x: NDArray[np.float64], b: float) -> NDArray[np.float64]:
            mu = float(np.mean(x))
            if kind == "LEFT":
                return _logit(mu - x + b)
            if kind == "MID":
                return _logit(-np.abs(x - mu) + 0.75 + b)
            if kind == "TAIL":
                return _logit(np.abs(x - mu) - 0.75 + b)
            return _logit(-mu + x + b)

        shift = _bin_search(prop, lambda b: float(np.mean(_formula(testset, b))))

        if score_vec.size == 1 or np.all(score_vec == score_vec[0]):
            probs = np.full(score_vec.shape, prop, dtype=np.float64)
        else:
            probs = _formula(score_vec, shift)

        draws = 1 - rng.binomial(1, np.clip(probs, 0.0, 1.0))
        r_temp = p.copy()
        r_temp[p == code] = draws
        r_temp[p != code] = 1
        out.append(r_temp)
    return out


def _weighted_sum_scores(
    p: NDArray[np.int_],
    data: NDArray[np.float64],
    weights: NDArray[np.float64],
    *,
    std: bool,
) -> list[NDArray[np.float64]]:
    n_pat = weights.shape[0]
    scores: list[NDArray[np.float64]] = []
    for i in range(n_pat):
        code = i + 2
        cand_mask = p == code
        if not np.any(cand_mask):
            scores.append(np.array([0.0], dtype=np.float64))
            continue
        candidates = data[cand_mask, :].astype(np.float64)
        if std and candidates.shape[0] > 1:
            col_std = np.std(candidates, axis=0, ddof=1)
            if np.any(col_std > 0):
                candidates = (candidates - np.mean(candidates, axis=0)) / np.where(
                    col_std > 0, col_std, 1.0
                )
        w = weights[i, :]
        scores.append((candidates * w).sum(axis=1))
    return scores


def ampute(
    data: NDArray[np.floating],
    *,
    prop: float = 0.5,
    patterns: NDArray[np.int_] | None = None,
    freq: NDArray[np.floating] | None = None,
    mech: str = "MCAR",
    weights: NDArray[np.floating] | None = None,
    std: bool = True,
    cont: bool = True,
    type: str | list[str] | None = None,
    bycases: bool = True,
    run: bool = True,
    seed: int | None = None,
) -> AmputeResult:
    """Introduce missing values into complete data (R ``ampute``)."""
    matrix = np.asarray(data, dtype=np.float64)
    if matrix.ndim != 2:
        raise ValueError("data must be a 2-D array")
    if np.any(~np.isfinite(matrix)):
        raise ValueError("data cannot contain missing values")
    if matrix.shape[1] < 2:
        raise ValueError("data should contain at least two columns")

    if prop > 1.0:
        prop = prop / 100.0
    if not 0.0 < prop < 1.0:
        raise ValueError("prop must be between 0 and 1")

    n_rows, n_cols = matrix.shape
    patterns_arr = np.asarray(
        patterns if patterns is not None else _default_patterns(n_cols),
        dtype=np.int_,
    )
    if patterns_arr.ndim == 1:
        if patterns_arr.size % n_cols != 0:
            raise ValueError("patterns vector length must be a multiple of ncol(data)")
        patterns_arr = patterns_arr.reshape(-1, n_cols)
    if patterns_arr.shape[1] != n_cols:
        raise ValueError("patterns must have ncol(data) columns")

    n_pat = patterns_arr.shape[0]
    freq_arr = np.asarray(freq if freq is not None else _default_freq(n_pat), dtype=np.float64)
    if freq_arr.shape != (n_pat,):
        raise ValueError("freq length must match number of patterns")
    freq_arr = freq_arr / np.sum(freq_arr)

    mech_u = mech.upper()
    if mech_u not in ("MCAR", "MAR", "MNAR"):
        raise ValueError("mech must be MCAR, MAR, or MNAR")

    weights_arr = None
    if mech_u != "MCAR":
        weights_arr = np.asarray(
            weights if weights is not None else _default_weights(patterns_arr, mech_u),
            dtype=np.float64,
        )
        if weights_arr.ndim == 1:
            weights_arr = weights_arr.reshape(-1, n_cols)
        if weights_arr.shape != (n_pat, n_cols):
            raise ValueError("weights must have shape (#patterns, #variables)")

    types = _default_type(n_pat)
    if type is not None:
        if isinstance(type, str):
            types = [type.upper()] * n_pat
        else:
            types = [t.upper() for t in type]
            if len(types) == 1:
                types = types * n_pat

    work_prop = float(prop)
    if not bycases:
        work_prop = _recalculate_prop_cellwise(work_prop, freq_arr, patterns_arr, n_rows, n_cols)

    rng = np.random.default_rng(seed)
    p = rng.choice(n_pat, size=n_rows, p=freq_arr) + 2

    scores_list: list[NDArray[np.float64]] | None = None
    amp: NDArray[np.float64] | None = None

    if run:
        amp = matrix.copy()
        if mech_u == "MCAR":
            r_list = _ampute_mcar(p, patterns_arr, work_prop, rng)
        else:
            scores_list = _weighted_sum_scores(p, matrix, weights_arr, std=std)
            if cont:
                r_list = _ampute_continuous(p, scores_list, round(work_prop, 3), types, rng)
            else:
                raise NotImplementedError("discrete amputation (cont=False) is not implemented")

        for i in range(n_pat):
            if not np.any(p == i + 2):
                continue
            row_amp = r_list[i] == 0
            col_amp = patterns_arr[i] == 0
            amp[np.ix_(row_amp, col_amp)] = np.nan

    return AmputeResult(
        amp=amp,
        patterns=patterns_arr,
        freq=freq_arr,
        mech=mech_u,
        prop=float(prop),
        bycases=bycases,
        weights=weights_arr,
        scores=scores_list,
        cand=p - 1,
        type_=types,
        cont=cont,
        data=matrix.copy(),
    )
