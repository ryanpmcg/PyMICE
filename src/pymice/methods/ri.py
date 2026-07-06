"""Random indicator imputation for non-ignorable sensitivity (ri)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.norm import impute_norm
from pymice.methods.registry import register_method


def impute_ri(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    ri: float = 0.5,
    **kwargs: object,
) -> NDArray[np.floating]:
    """
    Random indicator sensitivity imputation (R ``mice.impute.ri``).

    With probability ``ri``, imputations are shifted upward by one residual SD.
    """
    drawn = impute_norm(y, ry, x, wy, rng, **kwargs)
    y_obs = y[ry]
    sd = float(np.std(y_obs)) if y_obs.size else 1.0
    flip = rng.random(drawn.size) < float(ri)
    out = drawn.copy()
    out[flip] += sd
    return out


register_method("ri", impute_ri)
