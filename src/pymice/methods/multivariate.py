"""Helpers for multivariate imputation methods (jomoImpute, panImpute)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

# mitml / mice type codes
TYPE_TARGET = 1
TYPE_FIXED = 2
TYPE_RANDOM = 3
TYPE_GROUP = -1
TYPE_CLUSTER = -2
TYPE_OMIT = 0

MULTIVARIATE_METHODS = frozenset({"jomoImpute", "panImpute"})


@dataclass(frozen=True)
class JointModelSpec:
    """Parsed joint-model roles from a block ``type`` row."""

    targets: list[str]
    fixed: list[str]
    random: list[str]
    cluster: str | None
    group: str | None


def is_multivariate_method(name: str) -> bool:
    return name in MULTIVARIATE_METHODS


def parse_type_row(type_row: NDArray[np.int_], column_names: list[str]) -> JointModelSpec:
    """Parse mitml-style type vector (R ``.type2formula`` roles)."""
    if type_row.shape[0] != len(column_names):
        raise ValueError("type row length must match number of columns")

    targets: list[str] = []
    fixed: list[str] = []
    random: list[str] = []
    cluster: str | None = None
    group: str | None = None

    for code, name in zip(type_row.tolist(), column_names, strict=True):
        if code == TYPE_TARGET:
            targets.append(name)
        elif code == TYPE_FIXED:
            fixed.append(name)
        elif code == TYPE_RANDOM:
            random.append(name)
        elif code == TYPE_CLUSTER:
            if cluster is not None:
                raise ValueError("only one cluster indicator may be specified")
            cluster = name
        elif code == TYPE_GROUP:
            if group is not None:
                raise ValueError("only one grouping variable may be specified")
            group = name
        elif code == TYPE_OMIT:
            continue
        else:
            raise ValueError(f"unknown type code {code} for column '{name}'")

    if not targets:
        raise ValueError("at least one target variable (type=1) is required")
    return JointModelSpec(
        targets=targets,
        fixed=fixed,
        random=random,
        cluster=cluster,
        group=group,
    )


def single_to_imputes(
    completed: NDArray[np.float64],
    column_names: list[str],
    observed: NDArray[np.bool_],
    where: NDArray[np.bool_],
    block_vars: list[str],
) -> dict[str, NDArray[np.float64]]:
    """Extract imputation vectors for missing cells (R ``single2imputes``)."""
    out: dict[str, NDArray[np.float64]] = {}
    for name in block_vars:
        j = column_names.index(name)
        mask = (~observed[:, j]) & where[:, j]
        if not np.any(mask):
            continue
        out[name] = completed[mask, j].astype(np.float64, copy=False)
    return out


def prepare_block_data(
    data: NDArray[np.float64],
    column_names: list[str],
    block_vars: list[str],
    observed: NDArray[np.bool_],
    where: NDArray[np.bool_],
) -> NDArray[np.float64]:
    """Mask originally-missing block cells to NaN (R multivariate sampler)."""
    work = data.copy()
    block_set = set(block_vars)
    for name in block_set:
        j = column_names.index(name)
        mask = (~observed[:, j]) & where[:, j]
        work[mask, j] = np.nan
    return work
