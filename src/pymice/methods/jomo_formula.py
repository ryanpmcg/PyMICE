"""mitml-style type vectors and design-matrix construction for JOMO."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.multivariate import (
    TYPE_CLUSTER,
    TYPE_FIXED,
    TYPE_GROUP,
    TYPE_RANDOM,
    JointModelSpec,
    parse_type_row,
)


def build_design_matrices(
    work: NDArray[np.float64],
    column_names: list[str],
    spec: JointModelSpec,
) -> tuple[
    NDArray[np.float64] | None,
    NDArray[np.float64] | None,
    NDArray[np.int_] | None,
    NDArray[np.int_] | None,
]:
    """
    Extract fixed ``X``, random ``Z``, cluster, and group vectors from a block.

    Returns (x, z, clusters, groups); entries are ``None`` when not specified.
    """
    x = z = clusters = groups = None

    if spec.fixed:
        idx = [column_names.index(v) for v in spec.fixed]
        x = work[:, idx].astype(np.float64)
        if np.any(~np.isfinite(x)):
            raise ValueError("fixed predictors must be completely observed")
        x = np.column_stack([np.ones(work.shape[0]), x])

    if spec.random:
        idx = [column_names.index(v) for v in spec.random]
        z = work[:, idx].astype(np.float64)
        if np.any(~np.isfinite(z)):
            raise ValueError("random predictors must be completely observed")

    if spec.cluster is not None:
        cidx = column_names.index(spec.cluster)
        raw = work[:, cidx]
        if np.any(~np.isfinite(raw)):
            raise ValueError(f"cluster '{spec.cluster}' contains missing values")
        clusters = np.asarray(raw, dtype=np.int64)
        _, clusters = np.unique(clusters, return_inverse=True)
        clusters = clusters.astype(np.int_)

    if spec.group is not None:
        gidx = column_names.index(spec.group)
        raw = work[:, gidx]
        if np.any(~np.isfinite(raw)):
            raise ValueError(f"group '{spec.group}' contains missing values")
        groups = np.asarray(raw, dtype=np.int64)
        _, groups = np.unique(groups, return_inverse=True)
        groups = groups.astype(np.int_)

    return x, z, clusters, groups


def type_row_from_roles(
    column_names: list[str],
    *,
    targets: list[str],
    fixed: list[str] | None = None,
    random: list[str] | None = None,
    cluster: str | None = None,
    group: str | None = None,
) -> NDArray[np.int_]:
    """Build a mitml-compatible type row (R ``jomoImpute`` roles)."""
    codes = np.zeros(len(column_names), dtype=np.int_)
    for name in targets:
        codes[column_names.index(name)] = 1
    for name in fixed or []:
        codes[column_names.index(name)] = TYPE_FIXED
    for name in random or []:
        codes[column_names.index(name)] = TYPE_RANDOM
    if cluster is not None:
        codes[column_names.index(cluster)] = TYPE_CLUSTER
    if group is not None:
        codes[column_names.index(group)] = TYPE_GROUP
    parse_type_row(codes, column_names)
    return codes
