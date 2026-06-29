"""Core data types for the MICE engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass
class FitResult:
    """One complete-data model fit (coefficients + variances)."""

    terms: list[str]
    estimate: dict[str, float]
    variance: dict[str, float]
    df_residual: float
    n_obs: int


@dataclass
class Mira:
    """Multiply imputed repeated analysis (R ``mira``)."""

    m: int
    analyses: list[FitResult]
    call: str = ""


ImputationFits = Mira


@dataclass
class PoolResult:
    """Pooled MI estimates (R ``mipo``)."""

    m: int
    rule: str
    dfcom: float
    rows: list[dict[str, float | str]]

    def to_dataframe(self):
        """Return pooled estimates as a pandas DataFrame."""
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError("pandas is required for PoolResult.to_dataframe()") from exc
        return pd.DataFrame(self.rows)


class VariableKind(Enum):
    NUMERIC = "numeric"
    BINARY = "binary"
    UNORDERED = "unordered"
    ORDERED = "ordered"


@dataclass
class VariableSpec:
    name: str
    kind: VariableKind
    levels: tuple[Any, ...] = ()


@dataclass
class Mids:
    """Multiply imputed dataset (analogous to R ``mids``)."""

    data: NDArray[np.floating]
    column_names: list[str]
    imp: dict[str, NDArray[np.floating]]
    m: int
    where: NDArray[np.bool_]
    method: dict[str, str]
    predictor_matrix: NDArray[np.int_]
    visit_sequence: list[str]
    blocks: dict[str, list[str]]
    iteration: int
    seed: int | None
    nmis: dict[str, int]
    chain_mean: dict[str, NDArray[np.floating]] = field(default_factory=dict)
    chain_var: dict[str, NDArray[np.floating]] = field(default_factory=dict)
    ignore: NDArray[np.bool_] | None = None
    variable_specs: list[VariableSpec] = field(default_factory=list)
    block_predictor_matrix: dict[str, NDArray[np.int_]] | None = None
    post: dict[str, str] | None = None

    @property
    def n_obs(self) -> int:
        return int(self.data.shape[0])

    @property
    def n_vars(self) -> int:
        return int(self.data.shape[1])

    def summary(self) -> dict[str, object]:
        """Lightweight metadata summary (Pythonic alternative to R ``summary.mids``)."""
        return {
            "n_obs": self.n_obs,
            "n_vars": self.n_vars,
            "m": self.m,
            "iteration": self.iteration,
            "seed": self.seed,
            "nmis": dict(self.nmis),
            "methods": dict(self.method),
        }

    def continue_(self, *, max_iter: int = 5, verbose: bool = False, **kwargs: object) -> Mids:
        """Run additional Gibbs iterations (R ``mice.mids`` analogue)."""
        from pymice.continue_mids import continue_imputation

        return continue_imputation(self, max_iter=max_iter, verbose=verbose, **kwargs)
