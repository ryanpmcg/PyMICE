"""Build PyMICE inputs from WEPPCLIFF imputation DataFrames."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from pymice.imputation_setup import make_blocks, make_method, make_predictor_matrix
from pymice.integrations.weppcliff.constraints import non_negative_posts, temperature_posts
from pymice.quickpred import quickpred
from pymice.types import VariableKind, VariableSpec


def resolve_imp_method(
    imp_method: str,
    *,
    im_override: str = "DEFAULT",
    quick_impute: bool = False,
) -> tuple[str, int | None]:
    """Map WEPPCLIFF config to PyMICE method and optional maxit cap."""
    method = str(imp_method).lower()
    if str(im_override).upper() != "DEFAULT":
        method = str(im_override).lower()
    maxit_cap: int | None = None
    if quick_impute:
        method = "cart"
        maxit_cap = 10
    return method, maxit_cap


def adaptive_maxit(n_complete: int, n_total: int, io_cap: int) -> int:
    """R WEPPCLIFF formula: more missingness → more iterations (capped by ``io``)."""
    if n_total <= 0:
        return 20
    frac = n_complete / n_total
    return min(int(io_cap), max(20, int(np.ceil(100 - 100 * frac))))


def _encode_column(series: pd.Series, name: str) -> tuple[NDArray[np.float64], VariableSpec]:
    if str(series.dtype) == "category" or series.dtype == object:
        codes, uniques = pd.factorize(series, sort=True)
        codes = codes.astype(np.float64)
        codes[codes < 0] = np.nan
        if len(uniques) <= 2:
            return codes, VariableSpec(name=name, kind=VariableKind.BINARY, levels=(0.0, 1.0))
        levels = tuple(float(i) for i in range(len(uniques)))
        return codes, VariableSpec(name=name, kind=VariableKind.UNORDERED, levels=levels)
    vals = pd.to_numeric(series, errors="coerce").to_numpy(dtype=np.float64)
    return vals, VariableSpec(name=name, kind=VariableKind.NUMERIC)


def dataframe_to_matrix(
    df: pd.DataFrame,
    column_names: list[str],
) -> tuple[NDArray[np.float64], list[VariableSpec]]:
    cols: list[NDArray[np.float64]] = []
    specs: list[VariableSpec] = []
    for name in column_names:
        col, spec = _encode_column(df[name], name)
        cols.append(col)
        specs.append(spec)
    return np.column_stack(cols), specs


def build_mice_plan(
    df: pd.DataFrame,
    *,
    imp_method: str,
    io_cap: int = 100,
    quick_impute: bool = False,
    im_override: str = "DEFAULT",
    use_quickpred: bool = True,
    mincor: float = 0.2,
    minpuc: float = 0.05,
    partition: str = "scatter",
    seed: int = 42,
    skip_impute_columns: tuple[str, ...] = ("_YEAR_BLOCK_",),
) -> dict[str, Any]:
    """Assemble kwargs for ``pymice.mice()`` from a value-only DataFrame."""
    names = list(df.columns)
    matrix, specs = dataframe_to_matrix(df, names)
    where = np.isnan(matrix)
    n_complete = int(np.sum(np.all(~np.isnan(matrix), axis=1)))
    method_str, maxit_cap = resolve_imp_method(
        imp_method,
        im_override=im_override,
        quick_impute=quick_impute,
    )
    maxit = adaptive_maxit(n_complete, matrix.shape[0], io_cap)
    if maxit_cap is not None:
        maxit = min(maxit, maxit_cap)

    if use_quickpred and matrix.shape[1] > 1:
        pred = quickpred(
            matrix,
            mincor=mincor,
            minpuc=minpuc,
            column_names=names,
        )
    else:
        pred = make_predictor_matrix(names)

    blocks = make_blocks(names, partition=partition)
    methods = make_method(
        names,
        specs,
        where,
        blocks=blocks,
        method=method_str,
    )
    for skip in skip_impute_columns:
        if skip in methods:
            methods[skip] = ""
        j = names.index(skip) if skip in names else -1
        if j >= 0:
            where[:, j] = False

    post = {**temperature_posts(names), **non_negative_posts(names)}

    return {
        "data": matrix,
        "column_names": names,
        "variable_specs": specs,
        "m": 1,
        "maxit": maxit,
        "method": methods,
        "predictor_matrix": pred,
        "blocks": blocks,
        "post": post,
        "seed": seed,
    }
