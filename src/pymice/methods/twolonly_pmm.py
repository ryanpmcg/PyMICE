"""Level-2 PMM imputation (2lonly.pmm)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.registry import register_method
from pymice.methods.twolonly_core import imputation_level2


def impute_2lonly_pmm(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    type: NDArray[np.int_] | None = None,
    **kwargs: object,
) -> NDArray[np.floating]:
    """Impute level-2 data via aggregated predictive mean matching."""
    return imputation_level2(y, ry, x, wy, rng, type=type, method="pmm", **kwargs)


register_method("2lonly.pmm", impute_2lonly_pmm)
