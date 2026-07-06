"""MICE-specific mean imputation (micemean) — alias of ``mean``."""

from __future__ import annotations

from pymice.methods.mean import impute_mean
from pymice.methods.registry import register_method

register_method("micemean", impute_mean)
