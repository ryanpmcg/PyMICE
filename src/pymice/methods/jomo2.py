"""Level-2 target JOMO aliases (jomo2con / jomo2ran)."""

from __future__ import annotations

from pymice.methods.jomo_impute import impute_jomo
from pymice.methods.registry import register_multivariate_method

register_multivariate_method("jomo2con", impute_jomo)
register_multivariate_method("jomo2ran", impute_jomo)
