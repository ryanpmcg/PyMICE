"""Continue / extend an existing MICE run (R ``mice.mids`` analogue)."""

from __future__ import annotations

from typing import Any

from pymice.complete import complete
from pymice.engine import mice
from pymice.types import Mids


def continue_imputation(
    mids: Mids,
    *,
    max_iter: int = 5,
    verbose: bool = False,
    **kwargs: Any,
) -> Mids:
    """Warm-start additional Gibbs iterations from the last imputation draw."""
    if mids.m < 1:
        raise ValueError("cannot continue a mids object with m < 1")
    start = complete(mids, mids.m)
    if not isinstance(start, type(mids.data)):
        raise TypeError("expected ndarray from complete()")

    call_kwargs: dict[str, Any] = {
        "column_names": mids.column_names,
        "variable_specs": mids.variable_specs,
        "m": mids.m,
        "maxit": max_iter,
        "method": mids.method,
        "predictor_matrix": mids.predictor_matrix,
        "visit_sequence": mids.visit_sequence,
        "blocks": mids.blocks,
        "where": mids.where,
        "seed": mids.seed,
        "ignore": mids.ignore,
        "block_predictor_matrix": mids.block_predictor_matrix,
        "data_init": start,
        "verbose": verbose,
    }
    call_kwargs.update(kwargs)
    out = mice(start, **call_kwargs)
    out.iteration = mids.iteration + max_iter
    return out
