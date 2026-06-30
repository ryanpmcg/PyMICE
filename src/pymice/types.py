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
    rss: float | None = None


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

    def __repr__(self) -> str:
        lines = [
            "Class: Mids (Multiply Imputed Dataset)",
            f"Number of multiple imputations (m): {self.m}",
            f"Number of iterations: {self.iteration}",
            f"Seed: {self.seed}",
            f"Number of observations: {self.n_obs}",
            f"Number of variables: {self.n_vars}",
            "Imputation methods:",
        ]
        for col in self.column_names:
            meth = self.method.get(col, "")
            lines.append(f"  {col}: {meth if meth else '(none)'} ({self.nmis.get(col, 0)} missing)")
        return "\n".join(lines)

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


def ibind(x: Mids, y: Mids) -> Mids:
    """Combine two Mids objects by combining their imputations (R ``ibind``)."""
    if x.column_names != y.column_names:
        raise ValueError("Cannot combine Mids objects with different column names")
    if x.n_obs != y.n_obs:
        raise ValueError("Cannot combine Mids objects with different number of observations")
    if not np.array_equal(x.where, y.where):
        raise ValueError("Cannot combine Mids objects with different 'where' masks")

    new_imp = {}
    for col in x.column_names:
        x_imp = x.imp.get(col)
        y_imp = y.imp.get(col)
        if x_imp is not None and y_imp is not None:
            new_imp[col] = np.column_stack([x_imp, y_imp])
        elif x_imp is not None:
            new_imp[col] = x_imp.copy()
        elif y_imp is not None:
            new_imp[col] = y_imp.copy()

    new_chain_mean = {}
    new_chain_var = {}
    for col in x.column_names:
        x_mean = x.chain_mean.get(col)
        y_mean = y.chain_mean.get(col)
        if x_mean is not None and y_mean is not None:
            new_chain_mean[col] = np.column_stack([x_mean, y_mean])
        elif x_mean is not None:
            new_chain_mean[col] = x_mean.copy()
        elif y_mean is not None:
            new_chain_mean[col] = y_mean.copy()

        x_var = x.chain_var.get(col)
        y_var = y.chain_var.get(col)
        if x_var is not None and y_var is not None:
            new_chain_var[col] = np.column_stack([x_var, y_var])
        elif x_var is not None:
            new_chain_var[col] = x_var.copy()
        elif y_var is not None:
            new_chain_var[col] = y_var.copy()

    return Mids(
        data=x.data.copy(),
        column_names=list(x.column_names),
        imp=new_imp,
        m=x.m + y.m,
        where=x.where.copy(),
        method=dict(x.method),
        predictor_matrix=x.predictor_matrix.copy(),
        visit_sequence=list(x.visit_sequence),
        blocks=dict(x.blocks),
        iteration=max(x.iteration, y.iteration),
        seed=x.seed,
        nmis=dict(x.nmis),
        chain_mean=new_chain_mean,
        chain_var=new_chain_var,
        ignore=x.ignore.copy() if x.ignore is not None else None,
        variable_specs=list(x.variable_specs),
        block_predictor_matrix=x.block_predictor_matrix.copy() if x.block_predictor_matrix is not None else None,
        post=dict(x.post) if x.post is not None else None,
    )


def filter_imputations(mids: Mids, indices: int | list[int] | range | NDArray[np.int_]) -> Mids:
    """Subset the imputations of a Mids object by index (R subset/filter analogue)."""
    if isinstance(indices, (int, np.integer)):
        idx_list = [int(indices)]
    else:
        idx_list = [int(i) for i in indices]

    for idx in idx_list:
        if idx < 0 or idx >= mids.m:
            raise IndexError(f"Imputation index {idx} out of range for m={mids.m}")

    new_imp = {}
    for col, val in mids.imp.items():
        new_imp[col] = val[:, idx_list]

    new_chain_mean = {}
    new_chain_var = {}
    for col in mids.column_names:
        if col in mids.chain_mean:
            new_chain_mean[col] = mids.chain_mean[col][:, idx_list]
        if col in mids.chain_var:
            new_chain_var[col] = mids.chain_var[col][:, idx_list]

    return Mids(
        data=mids.data.copy(),
        column_names=list(mids.column_names),
        imp=new_imp,
        m=len(idx_list),
        where=mids.where.copy(),
        method=dict(mids.method),
        predictor_matrix=mids.predictor_matrix.copy(),
        visit_sequence=list(mids.visit_sequence),
        blocks=dict(mids.blocks),
        iteration=mids.iteration,
        seed=mids.seed,
        nmis=dict(mids.nmis),
        chain_mean=new_chain_mean,
        chain_var=new_chain_var,
        ignore=mids.ignore.copy() if mids.ignore is not None else None,
        variable_specs=list(mids.variable_specs),
        block_predictor_matrix=mids.block_predictor_matrix.copy() if mids.block_predictor_matrix is not None else None,
        post=dict(mids.post) if mids.post is not None else None,
    )
