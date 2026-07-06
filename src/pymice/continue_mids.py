"""Continue / extend an existing MICE run (R ``mice.mids`` analogue)."""

from __future__ import annotations

from typing import Any

import numpy as np

from pymice.complete import complete
from pymice.engine import mice
from pymice.types import Mids


def _merge_continue_state(prior: Mids, out: Mids) -> None:
    """Append prior chain diagnostics and logged events onto a continued run."""
    for name in out.column_names:
        prior_mean = prior.chain_mean.get(name)
        new_mean = out.chain_mean.get(name)
        if prior_mean is not None and new_mean is not None:
            out.chain_mean[name] = np.vstack([prior_mean, new_mean])

        prior_var = prior.chain_var.get(name)
        new_var = out.chain_var.get(name)
        if prior_var is not None and new_var is not None:
            out.chain_var[name] = np.vstack([prior_var, new_var])

    out.logged_events = list(prior.logged_events) + list(out.logged_events)


def continue_imputation(
    mids: Mids,
    *,
    maxit: int = 5,
    max_iter: int | None = None,
    print: bool = False,
    print_flag: bool | None = None,
    verbose: bool | None = None,
    **kwargs: Any,
) -> Mids:
    """Warm-start additional Gibbs iterations from the last imputation draw (R ``mice.mids``)."""
    from pymice.r_compat import resolve_maxit, resolve_print_flag

    iterations = resolve_maxit(maxit=maxit, max_iter=max_iter)
    silent = resolve_print_flag(
        print=print,
        print_flag=print_flag,
        verbose=verbose,
    )

    if mids.m < 1:
        raise ValueError("cannot continue a mids object with m < 1")
    start = complete(mids, mids.m, as_dataframe=False)
    if not isinstance(start, np.ndarray):
        raise TypeError("expected ndarray from complete()")

    call_kwargs: dict[str, Any] = {
        "column_names": mids.column_names,
        "variable_specs": mids.variable_specs,
        "m": mids.m,
        "maxit": iterations,
        "method": mids.method,
        "predictor_matrix": mids.predictor_matrix,
        "visit_sequence": mids.visit_sequence,
        "blocks": mids.blocks,
        "where": mids.where,
        "seed": mids.seed,
        "rng": mids.rng_backend,
        "ignore": mids.ignore,
        "block_predictor_matrix": mids.block_predictor_matrix,
        "data_init": start,
        "print": silent,
    }
    call_kwargs.update(kwargs)
    out = mice(start, **call_kwargs)
    _merge_continue_state(mids, out)
    out.iteration = mids.iteration + iterations
    return out
