"""Random Forest imputation method (R ``mice.impute.rf`` equivalent)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.registry import register_method


def _sklearn_ensemble():
    try:
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "The rf method requires scikit-learn. Install with: pip install pymice[ml]"
        ) from exc
    return RandomForestClassifier, RandomForestRegressor


def _prepare_x(x: NDArray[np.floating]) -> NDArray[np.float64]:
    """Ensure at least one predictor column (intercept if empty)."""
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    if arr.shape[1] == 0:
        arr = np.ones((arr.shape[0], 1), dtype=np.float64)
    return arr


def _impute_regression(
    yobs: NDArray[np.float64],
    xobs: NDArray[np.float64],
    xmis: NDArray[np.float64],
    rng: np.random.Generator,
    *,
    n_estimators: int,
    min_samples_leaf: int,
) -> NDArray[np.float64]:
    """Draw continuous values from random forest trees."""
    _, RandomForestRegressor = _sklearn_ensemble()
    forest = RandomForestRegressor(
        n_estimators=n_estimators,
        min_samples_leaf=min_samples_leaf,
        random_state=rng.integers(0, 2**31 - 1),
    )
    forest.fit(xobs, yobs)

    # Extract prediction from a randomly chosen tree in the forest for each missing case
    # This acts as a Bayesian-like bootstrap draw from the forest posterior
    preds = np.column_stack([tree.predict(xmis) for tree in forest.estimators_])
    out = np.empty(xmis.shape[0], dtype=np.float64)
    for i in range(xmis.shape[0]):
        out[i] = float(rng.choice(preds[i]))
    return out


def _impute_classification(
    yobs: NDArray[np.float64],
    xobs: NDArray[np.float64],
    xmis: NDArray[np.float64],
    rng: np.random.Generator,
    *,
    n_estimators: int,
    min_samples_leaf: int,
    levels: tuple[float, ...] | None,
) -> NDArray[np.float64]:
    """Draw class labels from random forest probability distributions."""
    RandomForestClassifier, _ = _sklearn_ensemble()

    if levels is None:
        levels_tuple = tuple(float(v) for v in np.unique(yobs))
    else:
        levels_tuple = tuple(float(v) for v in levels)

    level_to_code = {lv: i for i, lv in enumerate(levels_tuple)}
    counts = np.array([int(np.sum(yobs == lv)) for lv in levels_tuple])
    if np.any(counts == yobs.size):
        level = levels_tuple[int(np.argmax(counts == yobs.size))]
        return np.full(xmis.shape[0], level, dtype=np.float64)

    y_codes = np.array([level_to_code[v] for v in yobs], dtype=np.int_)
    forest = RandomForestClassifier(
        n_estimators=n_estimators,
        min_samples_leaf=min_samples_leaf,
        random_state=rng.integers(0, 2**31 - 1),
    )
    forest.fit(xobs, y_codes)
    proba = forest.predict_proba(xmis)
    class_index = {int(c): i for i, c in enumerate(forest.classes_)}

    out = np.empty(xmis.shape[0], dtype=np.float64)
    for i in range(xmis.shape[0]):
        p = proba[i]
        code = int(rng.choice(forest.classes_, p=p))
        out[i] = levels_tuple[class_index[code]]
    return out


def impute_rf(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    rfiter: int = 10,
    minbucket: int = 5,
    levels: tuple[float, ...] | None = None,
    classification: bool | None = None,
    **_: object,
) -> NDArray[np.floating]:
    """Impute via Random Forests (R ``mice.impute.rf`` equivalent)."""
    n_estimators = max(1, int(rfiter))
    min_samples_leaf = max(1, int(minbucket))

    y_arr = np.asarray(y, dtype=np.float64)
    x_arr = _prepare_x(x)
    yobs = y_arr[ry]
    xobs = x_arr[ry]
    xmis = x_arr[wy]

    if yobs.size == 0:
        raise ValueError("No observed values available for Random Forest imputation")

    use_classification = classification
    if use_classification is None:
        uniq = np.unique(yobs)
        use_classification = levels is not None or (
            uniq.size <= 10 and np.allclose(uniq, np.round(uniq))
        )

    if use_classification:
        return _impute_classification(
            yobs,
            xobs,
            xmis,
            rng,
            n_estimators=n_estimators,
            min_samples_leaf=min_samples_leaf,
            levels=levels,
        )
    return _impute_regression(
        yobs,
        xobs,
        xmis,
        rng,
        n_estimators=n_estimators,
        min_samples_leaf=min_samples_leaf,
    )


register_method("rf", impute_rf)
