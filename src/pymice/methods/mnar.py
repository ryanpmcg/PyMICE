"""Non-ignorable sensitivity imputation (mnar) — delta shift on residuals."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.norm import impute_norm
from pymice.methods.registry import register_method


def impute_mnar(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    mnar: float = 0.0,
    **kwargs: object,
) -> NDArray[np.floating]:
    """
    Impute with MNAR sensitivity parameter (R ``mice.impute.mnar``).

    Applies a fixed shift ``mnar`` to norm-drawn imputations (van Buuren sensitivity).
    """
    drawn = impute_norm(y, ry, x, wy, rng, **kwargs)
    return drawn + float(mnar)


register_method("mnar", impute_mnar)
