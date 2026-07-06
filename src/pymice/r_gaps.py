"""R ``mice`` features not yet ported — explicit ``NotImplementedError`` boundaries."""

from __future__ import annotations

from typing import NoReturn

from pymice.passive import is_passive

# Imputation methods documented in R ``mice()`` but not registered in PyMICE.
# Keys are lowercase for case-insensitive lookup.
UNIMPLEMENTED_IMPUTATION_METHODS: dict[str, str] = {}

# Top-level R utilities that intentionally have no PyMICE analogue yet.
UNIMPLEMENTED_FEATURES: dict[str, str] = {}


def unimplemented_imputation_methods() -> list[str]:
    """Return sorted R imputation method names that raise ``NotImplementedError``."""
    canonical = sorted(
        {name for name in UNIMPLEMENTED_IMPUTATION_METHODS if name != "2lmer"},
        key=str.lower,
    )
    return canonical


def unimplemented_features() -> list[str]:
    """Return sorted top-level R features that raise ``NotImplementedError``."""
    return sorted(UNIMPLEMENTED_FEATURES)


def _lookup_method_message(method: str) -> str | None:
    return UNIMPLEMENTED_IMPUTATION_METHODS.get(method.lower())


def ensure_imputation_method_available(method: str) -> None:
    """Raise ``NotImplementedError`` for known-but-unported R imputation methods."""
    if not method or is_passive(method):
        return
    message = _lookup_method_message(method)
    if message is not None:
        raise NotImplementedError(message)


def raise_not_implemented(feature: str) -> NoReturn:
    """Raise a clear ``NotImplementedError`` for a named R feature stub."""
    message = UNIMPLEMENTED_FEATURES.get(feature)
    if message is None:
        raise KeyError(f"unknown unimplemented feature: {feature!r}")
    raise NotImplementedError(message)


def as_mids(*args: object, **kwargs: object):
    """Construct a ``Mids`` object from components (R ``as.mids()``)."""
    from pymice.mids_construct import as_mids as _as_mids

    return _as_mids(*args, **kwargs)


def cbind_mids(*args: object, **kwargs: object):
    """Bind columns onto a ``Mids`` object (R ``cbind.mids()``)."""
    from pymice.mids_construct import cbind_mids as _cbind_mids

    return _cbind_mids(*args, **kwargs)


def rbind_mids(*args: object, **kwargs: object):
    """Bind rows onto a ``Mids`` object (R ``rbind.mids()``)."""
    from pymice.mids_construct import rbind_mids as _rbind_mids

    return _rbind_mids(*args, **kwargs)
