"""Missing data pattern table and visualization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass
class MdPatternResult:
    """Missingness pattern matrix (R ``md.pattern`` output)."""

    matrix: NDArray[np.int_]
    column_names: list[str]
    pattern_counts: list[int]
    column_missing: dict[str, int]

    @property
    def n_patterns(self) -> int:
        return len(self.pattern_counts)


def md_pattern(
    data: NDArray[np.floating] | Any,
    column_names: list[str] | None = None,
    *,
    plot: bool = False,
    rotate_names: bool = False,
    ax: Any | None = None,
) -> MdPatternResult:
    """
    Compute missing-data patterns (1=observed, 0=missing; R ``md.pattern``).

    Pass ``plot=True`` to draw the R-style pattern grid (R defaults to
    ``plot=TRUE``; PyMICE keeps ``plot=False`` unless requested).
    """
    from pymice.data_input import prepare_tabular_input

    matrix, names = prepare_tabular_input(data, column_names)
    if matrix.ndim != 2 or matrix.shape[1] < 2:
        raise ValueError("data must be a matrix with at least two columns")

    n_rows, _n_cols = matrix.shape
    data = matrix

    missing = np.isnan(data)
    nmis = missing.sum(axis=0)
    # R orders columns by ascending missing count; ties keep original column order.
    col_order = np.lexsort((np.arange(len(names)), nmis))
    missing = missing[:, col_order]
    ordered_names = [names[j] for j in col_order]

    if n_rows == 1:
        mpat = missing.copy()
    else:
        pat_strings = np.array(
            ["".join(str(int(v)) for v in row) for row in missing],
            dtype=object,
        )
        sort_idx = np.argsort(pat_strings, kind="stable")
        sorted_missing = missing[sort_idx]
        _, unique_idx = np.unique(sorted_missing, axis=0, return_index=True)
        mpat = sorted_missing[np.sort(unique_idx)]

    pattern_keys = np.array(
        ["".join(str(int(v)) for v in row) for row in mpat],
        dtype=object,
    )
    all_pats = np.array(["".join(str(int(v)) for v in row) for row in missing])
    counts = [int(np.sum(all_pats == key)) for key in pattern_keys]

    observed = (~mpat).astype(np.int_)
    row_totals = mpat.astype(np.int_).sum(axis=1, keepdims=True)
    body = np.hstack([observed, row_totals])

    footer_counts = nmis[col_order].astype(np.int_)
    footer = np.hstack([footer_counts, np.array([int(nmis.sum())], dtype=np.int_)])
    matrix = np.vstack([body, footer.reshape(1, -1)])

    col_missing = {name: int(nmis[col_order[i]]) for i, name in enumerate(ordered_names)}

    result = MdPatternResult(
        matrix=matrix,
        column_names=ordered_names,
        pattern_counts=counts,
        column_missing=col_missing,
    )

    if plot:
        from pymice.diagnostics.plots import plot_md_pattern

        plot_md_pattern(result, rotate_names=rotate_names, ax=ax)

    return result
