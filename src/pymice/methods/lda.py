"""Linear discriminant analysis imputation (lda)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept
from pymice.methods.registry import register_method
from pymice.methods.sklearn_backend import use_sklearn_backend


def _lda_impute(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
) -> NDArray[np.floating]:
    y_obs = y[ry].astype(np.int64)
    x_obs = add_intercept(np.asarray(x, dtype=np.float64)[ry])
    classes = np.unique(y_obs)
    if classes.size < 2:
        return np.full(int(np.sum(wy)), float(classes[0]), dtype=np.float64)

    if use_sklearn_backend():
        try:
            from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

            clf = LinearDiscriminantAnalysis()
            clf.fit(x_obs[:, 1:], y_obs)
            x_mis = np.asarray(x, dtype=np.float64)[wy]
            probs = clf.predict_proba(x_mis)
            draws = np.array(
                [rng.choice(classes, p=probs[i]) for i in range(probs.shape[0])],
                dtype=np.float64,
            )
            return draws
        except Exception:
            pass

    from pymice.methods.polyreg import impute_polyreg

    return impute_polyreg(y, ry, x, wy, rng, levels=tuple(float(c) for c in classes))


def impute_lda(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    levels: tuple[float, ...] | None = None,
    **_: object,
) -> NDArray[np.floating]:
    """Impute unordered categorical data via LDA (R ``mice.impute.lda``)."""
    del levels
    return _lda_impute(y, ry, x, wy, rng)


register_method("lda", impute_lda)
