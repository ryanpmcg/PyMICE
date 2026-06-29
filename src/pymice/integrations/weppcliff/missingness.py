"""Classify missingness patterns for adaptive imputation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import pandas as pd


class MissingnessKind(str, Enum):
    NONE = "none"
    SHORT_GAPS = "short_gaps"
    LONG_GAP_ALL = "long_gap_all"
    PERSISTENT_SEASONAL = "persistent_seasonal"
    VARIABLE_ABSENT = "variable_absent"
    MIXED = "mixed"


@dataclass
class MissingnessProfile:
    kinds: set[MissingnessKind] = field(default_factory=set)
    absent_variables: list[str] = field(default_factory=list)
    sparse_clusters: list[int] = field(default_factory=list)
    long_gap_fraction: float = 0.0
    primary: MissingnessKind = MissingnessKind.NONE

    def recommend_adjacent_pooling(self) -> bool:
        return MissingnessKind.PERSISTENT_SEASONAL in self.kinds or bool(self.sparse_clusters)

    def recommend_prior(self) -> bool:
        return (
            MissingnessKind.LONG_GAP_ALL in self.kinds
            or MissingnessKind.VARIABLE_ABSENT in self.kinds
            or MissingnessKind.PERSISTENT_SEASONAL in self.kinds
        )


def _longest_na_run(mask: np.ndarray) -> int:
    if mask.size == 0:
        return 0
    best = cur = 0
    for v in mask:
        if v:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def classify_missingness(
    df: pd.DataFrame,
    value_cols: list[str],
    *,
    cluster_col: str = "CLUSTER",
    n_min: int = 30,
) -> MissingnessProfile:
    """Inspect NA structure and suggest resilience strategies."""
    profile = MissingnessProfile()
    if not value_cols or df.empty:
        return profile

    sub = df[value_cols]
    if not sub.isna().any().any():
        return profile

    for col in value_cols:
        if sub[col].isna().all():
            profile.absent_variables.append(col)
            profile.kinds.add(MissingnessKind.VARIABLE_ABSENT)

    row_na = sub.isna().all(axis=1).to_numpy()
    if row_na.any():
        run = _longest_na_run(row_na)
        profile.long_gap_fraction = float(run / max(len(df), 1))
        if profile.long_gap_fraction >= 0.15:
            profile.kinds.add(MissingnessKind.LONG_GAP_ALL)

    if cluster_col in df.columns:
        for cid in df[cluster_col].dropna().unique():
            locs = df.index[df[cluster_col] == cid]
            complete = sub.loc[locs].notna().all(axis=1).sum()
            if int(complete) < n_min:
                profile.sparse_clusters.append(int(cid))
        if profile.sparse_clusters:
            profile.kinds.add(MissingnessKind.PERSISTENT_SEASONAL)

    if not profile.kinds:
        profile.kinds.add(MissingnessKind.SHORT_GAPS)

    if len(profile.kinds) > 1:
        profile.primary = MissingnessKind.MIXED
    else:
        profile.primary = next(iter(profile.kinds))

    return profile
