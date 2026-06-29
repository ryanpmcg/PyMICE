"""Default predictor matrix, methods, blocks, and visit sequence."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
from numpy.typing import NDArray

from pymice.enums import BlockPartition, ImputationMethod
from pymice.passive import is_passive
from pymice.passive_formula import PassiveFormula
from pymice.types import VariableKind, VariableSpec

DEFAULT_METHODS = ("pmm", "logreg", "polyreg", "polr")


def make_blocks(
    column_names: list[str] | dict[str, list[str]] | list[list[str]],
    *,
    partition: str | BlockPartition = "scatter",
) -> dict[str, list[str]]:
    """Create imputation blocks (R ``make.blocks``).

    Parameters
    ----------
    column_names
        Variable names, a user block dict, or a list of variable lists.
    partition
        When ``column_names`` is a flat list: ``scatter`` (one var per block),
        ``collect`` (single joint block), or ``void`` (no blocks).
    """
    if isinstance(column_names, dict):
        return name_blocks(column_names)
    if isinstance(column_names, list) and column_names and isinstance(column_names[0], list):
        return name_blocks({f"B{i + 1}": block for i, block in enumerate(column_names)})
    names = list(column_names)
    if isinstance(partition, BlockPartition):
        partition = partition.value
    if partition == "scatter":
        return {name: [name] for name in names}
    if partition == "collect":
        return {"collect": names}
    if partition == "void":
        return {}
    raise ValueError(f"Unknown partition: {partition}")


def name_blocks(
    blocks: dict[str, list[str]] | list[list[str]],
    *,
    prefix: str = "B",
) -> dict[str, list[str]]:
    """Name unnamed block entries (R ``name.blocks``)."""
    if isinstance(blocks, list):
        items = list(blocks)
        names: list[str] = [""] * len(items)
    else:
        items = [blocks[k] for k in blocks]
        names = list(blocks.keys())

    out: dict[str, list[str]] = {}
    inc = 1
    for name, variables in zip(names, items, strict=True):
        vars_list = list(variables)
        if name:
            out[name] = vars_list
            continue
        if len(vars_list) == 1:
            out[vars_list[0]] = vars_list
        else:
            out[f"{prefix}{inc}"] = vars_list
            inc += 1
    return out


def check_blocks(blocks: dict[str, list[str]], column_names: list[str]) -> dict[str, list[str]]:
    """Validate block variable names against ``column_names`` (R ``check.blocks``)."""
    named = name_blocks(blocks)
    found = set(column_names)
    missing = sorted({v for vars_ in named.values() for v in vars_} - found)
    if missing:
        raise ValueError(f"The following names were not found in data: {', '.join(missing)}")
    return named


def make_predictor_matrix(
    column_names: list[str],
    blocks: dict[str, list[str]] | None = None,
) -> NDArray[np.int_]:
    """Square predictor matrix: all columns predict each target except self."""
    n = len(column_names)
    matrix = np.ones((n, n), dtype=np.int_)
    np.fill_diagonal(matrix, 0)
    return matrix


def make_block_predictor_matrix(
    column_names: list[str],
    blocks: dict[str, list[str]],
) -> dict[str, NDArray[np.int_]]:
    """Block-row type/predictor matrix (R ``make.predictorMatrix`` with blocks)."""
    n = len(column_names)
    out: dict[str, NDArray[np.int_]] = {}
    for block_name, block_vars in blocks.items():
        row = np.ones(n, dtype=np.int_)
        if len(block_vars) == 1:
            j = column_names.index(block_vars[0])
            row[j] = 0
        out[block_name] = row
    return out


def make_visit_sequence(
    column_names: list[str],
    blocks: dict[str, list[str]] | None = None,
    order: str = "roman",
) -> list[str]:
    """Return block visit order (default: left-to-right / column order)."""
    blocks = blocks or make_blocks(column_names)
    names = list(blocks.keys())
    if order == "arabic":
        return list(reversed(names))
    if order not in ("roman", "monotone", "revmonotone"):
        raise ValueError(f"Unknown visit sequence order: {order}")
    return names


def make_method(
    column_names: list[str],
    specs: list[VariableSpec],
    where: NDArray[np.bool_],
    blocks: dict[str, list[str]] | None = None,
    method: str | Mapping[str, str] | None = None,
    default_method: tuple[str, str, str, str] = DEFAULT_METHODS,
) -> dict[str, str]:
    """Assign an imputation method to each block."""
    blocks = blocks or make_blocks(column_names)
    result: dict[str, str] = {}

    if method is None:
        method_map: dict[str, str] = {}
    elif isinstance(method, str):
        method_map = {name: _coerce_method_value(method) for name in column_names}
    else:
        method_map = {k: _coerce_method_value(v) for k, v in dict(method).items()}

    for block_name, block_vars in blocks.items():
        needs_imputation = any(np.any(where[:, column_names.index(var)]) for var in block_vars)
        if not needs_imputation:
            result[block_name] = ""
            continue

        if block_name in method_map:
            result[block_name] = method_map[block_name]
            continue

        assigned = ""
        for var in block_vars:
            if var in method_map:
                assigned = method_map[var]
                break
        if assigned:
            result[block_name] = assigned
            continue

        primary = block_vars[0]
        idx = column_names.index(primary)
        result[block_name] = default_method[_assign_method_index(specs[idx])]
    return result


def _coerce_method_value(value: str | ImputationMethod | PassiveFormula) -> str:
    if isinstance(value, ImputationMethod):
        return value.value
    if isinstance(value, PassiveFormula):
        return str(value)
    return str(value)


def _assign_method_index(spec: VariableSpec) -> int:
    """Map variable type to ``default_method`` index (R ``assign.method``)."""
    if spec.kind == VariableKind.NUMERIC:
        return 0
    if spec.kind == VariableKind.BINARY:
        return 1
    if spec.kind == VariableKind.UNORDERED:
        return 2
    return 3


def predictor_row_for_block(
    block_name: str,
    column_names: list[str],
    predictor_matrix: NDArray[np.int_],
    blocks: dict[str, list[str]],
    block_predictor_matrix: dict[str, NDArray[np.int_]] | None = None,
) -> NDArray[np.int_]:
    """Return predictor/type flags for a block."""
    if block_predictor_matrix is not None and block_name in block_predictor_matrix:
        return np.asarray(block_predictor_matrix[block_name], dtype=np.int_)
    if predictor_matrix.shape[0] == len(blocks):
        block_names = list(blocks.keys())
        if block_name in block_names:
            row = int(block_names.index(block_name))
            return np.asarray(predictor_matrix[row, :], dtype=np.int_)
    first_var = blocks[block_name][0]
    idx = column_names.index(first_var)
    return predictor_matrix[idx, :]


def registered_univariate_methods() -> set[str]:
    """Methods handled by the univariate sampler path."""
    from pymice.methods.registry import is_multivariate_method, registered_methods

    return {
        name
        for name in registered_methods()
        if not is_passive(name) and not is_multivariate_method(name)
    }
