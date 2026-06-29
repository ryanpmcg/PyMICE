"""Initialize imputation storage before the Gibbs sampler runs."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.registry import get_method


def where_indices(where_col: NDArray[np.bool_]) -> NDArray[np.int_]:
    """Row indices where the ``where`` mask is True for a column."""
    return np.where(where_col)[0]


def initialize_imputations(
    data: NDArray[np.float64],
    column_names: list[str],
    m: int,
    where: NDArray[np.bool_],
    observed: NDArray[np.bool_],
    ignore: NDArray[np.bool_],
    blocks: dict[str, list[str]],
    visit_sequence: list[str],
    method: dict[str, str],
    rng: np.random.Generator,
    data_init: NDArray[np.float64] | None = None,
) -> dict[str, NDArray[np.float64]]:
    """Create per-column imputation matrices and initial draws."""
    imp: dict[str, NDArray[np.float64]] = {}
    n_rows = data.shape[0]

    for block in visit_sequence:
        meth = method[block]
        for name in blocks[block]:
            j = column_names.index(name)
            widx = where_indices(where[:, j])
            if widx.size == 0:
                continue
            imp[name] = np.full((widx.size, m), np.nan, dtype=np.float64)
            if meth == "":
                continue

            y = data[:, j]
            ry = observed[:, j] & ~ignore
            sample_fn = get_method("sample")
            wy = where[:, j]

            for i in range(m):
                if data_init is not None:
                    imp[name][:, i] = data_init[widx, j]
                elif np.any(ry):
                    drawn = sample_fn(
                        y=y,
                        ry=ry,
                        x=np.empty((n_rows, 0)),
                        wy=wy,
                        rng=rng,
                    )
                    imp[name][:, i] = drawn
                else:
                    imp[name][:, i] = rng.normal(size=widx.size)

    return imp
