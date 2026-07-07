"""Classification and regression tree imputation (R ``mice.impute.cart``)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.registry import register_method


def _sklearn_trees():
    try:
        from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    except ImportError as exc:  # pragma: no cover - exercised via importorskip in tests
        raise ImportError(
            "The cart method requires scikit-learn. Install with: pip install pymice-fcs[ml]"
        ) from exc
    return DecisionTreeClassifier, DecisionTreeRegressor


def _prepare_x(x: NDArray[np.floating]) -> NDArray[np.float64]:
    """Match R: ensure at least one predictor column (intercept if empty)."""
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
    minbucket: int,
) -> NDArray[np.float64]:
    """Sample observed ``y`` values from the same terminal node (R ``method='anova'``)."""
    _, DecisionTreeRegressor = _sklearn_trees()
    tree = DecisionTreeRegressor(min_samples_leaf=minbucket)
    tree.fit(xobs, yobs)
    leaf_obs = tree.apply(xobs)
    leaf_mis = tree.apply(xmis)
    out = np.empty(leaf_mis.shape[0], dtype=np.float64)
    for i, leaf in enumerate(leaf_mis):
        donors = yobs[leaf_obs == leaf]
        if donors.size == 0:
            donors = yobs
        out[i] = float(rng.choice(donors))
    return out


def _impute_classification(
    yobs: NDArray[np.float64],
    xobs: NDArray[np.float64],
    xmis: NDArray[np.float64],
    rng: np.random.Generator,
    *,
    minbucket: int,
    levels: tuple[float, ...] | None,
) -> NDArray[np.float64]:
    """Draw class labels from terminal-node probabilities (R ``method='class'``)."""
    DecisionTreeClassifier, _ = _sklearn_trees()

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
    tree = DecisionTreeClassifier(min_samples_leaf=minbucket)
    tree.fit(xobs, y_codes)
    proba = tree.predict_proba(xmis)
    class_index = {int(c): i for i, c in enumerate(tree.classes_)}

    out = np.empty(xmis.shape[0], dtype=np.float64)
    for i in range(xmis.shape[0]):
        p = proba[i]
        code = int(rng.choice(tree.classes_, p=p))
        out[i] = levels_tuple[class_index[code]]
    return out


def impute_cart(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    minbucket: int = 5,
    cp: float = 1e-4,
    levels: tuple[float, ...] | None = None,
    classification: bool | None = None,
    **_: object,
) -> NDArray[np.floating]:
    """Impute via classification/regression trees (R ``mice.impute.cart``).

    Numeric targets sample observed values from the same terminal node.
    Categorical targets sample classes from predicted node probabilities.
    """
    del cp  # rpart complexity parameter; sklearn pruning deferred
    minbucket = max(1, int(minbucket))

    y_arr = np.asarray(y, dtype=np.float64)
    x_arr = _prepare_x(x)
    yobs = y_arr[ry]
    xobs = x_arr[ry]
    xmis = x_arr[wy]

    if yobs.size == 0:
        raise ValueError("No observed values available for cart imputation")

    use_classification = classification
    if use_classification is None:
        uniq = np.unique(yobs)
        use_classification = levels is not None or (
            uniq.size <= 10 and np.allclose(uniq, np.round(uniq))
        )

    if use_classification:
        return _impute_classification(yobs, xobs, xmis, rng, minbucket=minbucket, levels=levels)
    return _impute_regression(yobs, xobs, xmis, rng, minbucket=minbucket)


register_method("cart", impute_cart)
