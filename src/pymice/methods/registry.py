"""Method registry — maps method name to imputation callable."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

ImputeFn = Callable[..., NDArray[np.floating]]
MultivariateImputeFn = Callable[..., dict[str, NDArray[np.float64]]]

_REGISTRY: dict[str, ImputeFn] = {}
_MULTIVARIATE_REGISTRY: dict[str, MultivariateImputeFn] = {}


def register_method(name: str, fn: ImputeFn) -> None:
    if not name:
        raise ValueError("method name cannot be empty")
    _REGISTRY[name] = fn


def register_multivariate_method(name: str, fn: MultivariateImputeFn) -> None:
    if not name:
        raise ValueError("method name cannot be empty")
    _MULTIVARIATE_REGISTRY[name] = fn


def is_multivariate_method(name: str) -> bool:
    return name in _MULTIVARIATE_REGISTRY


def get_method(name: str) -> ImputeFn:
    if name not in _REGISTRY:
        raise ValueError(
            f"Unknown imputation method '{name}'. Registered methods: {sorted(_REGISTRY)}"
        )
    return _REGISTRY[name]


def get_multivariate_method(name: str) -> MultivariateImputeFn:
    if name not in _MULTIVARIATE_REGISTRY:
        raise ValueError(
            f"Unknown multivariate imputation method '{name}'. "
            f"Registered methods: {sorted(_MULTIVARIATE_REGISTRY)}"
        )
    return _MULTIVARIATE_REGISTRY[name]


def registered_methods() -> list[str]:
    return sorted(set(_REGISTRY) | set(_MULTIVARIATE_REGISTRY))
