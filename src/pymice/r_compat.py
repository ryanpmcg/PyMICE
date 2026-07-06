"""R ``mice`` naming aliases and keyword normalization."""

from __future__ import annotations

import warnings
from typing import Any

MICE_KW_ALIASES: dict[str, str] = {
    "predictorMatrix": "predictor_matrix",
    "visitSequence": "visit_sequence",
    "defaultMethod": "default_method",
    "dataInit": "data_init",
    "printFlag": "print",
    "blockPredictorMatrix": "block_predictor_matrix",
    "n.core": "n_jobs",
    "n_core": "n_jobs",
    "parallelseed": "parallelseed",
    "RNG": "rng",
}


def normalize_mice_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Map R-style camelCase keyword names to PyMICE snake_case."""
    out: dict[str, Any] = {}
    for key, value in kwargs.items():
        target = MICE_KW_ALIASES.get(key, key)
        if target in out and out[target] is not value:
            raise TypeError(f"duplicate keyword argument for {target!r}")
        out[target] = value
    return out


def resolve_print_flag(
    *,
    print: bool = False,
    print_flag: bool | None = None,
    printFlag: bool | None = None,
    verbose: bool | None = None,
) -> bool:
    """Resolve R ``print`` / legacy ``print_flag`` / ``verbose``."""
    if verbose is not None:
        warnings.warn(
            "verbose is deprecated; use print=False",
            DeprecationWarning,
            stacklevel=3,
        )
        return verbose
    if print_flag is not None:
        warnings.warn(
            "print_flag is deprecated; use print=False",
            DeprecationWarning,
            stacklevel=3,
        )
        return print_flag
    if printFlag is not None:
        warnings.warn(
            "printFlag is deprecated; use print=False",
            DeprecationWarning,
            stacklevel=3,
        )
        return printFlag
    return print


def resolve_maxit(*, maxit: int, max_iter: int | None) -> int:
    if max_iter is not None:
        warnings.warn(
            "max_iter is deprecated; use maxit=",
            DeprecationWarning,
            stacklevel=3,
        )
        return max_iter
    return maxit
