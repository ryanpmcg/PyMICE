"""Optional scikit-learn backend for ``lasso.*`` and ``lda`` imputation."""

from __future__ import annotations

import importlib.util
import os
from functools import lru_cache


def use_sklearn_backend(explicit: bool | None = None) -> bool:
    """Return whether to use scikit-learn (auto when ``[ml]`` extra installed)."""
    env = os.environ.get("PYMICE_SKLEARN", "").strip().lower()
    if env in {"0", "false", "no"}:
        return False
    if explicit is False:
        return False
    if explicit is True or env in {"1", "true", "yes"}:
        return sklearn_available()
    return sklearn_available()


@lru_cache(maxsize=1)
def sklearn_available() -> bool:
    return importlib.util.find_spec("sklearn") is not None
