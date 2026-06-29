"""Tests for imputation blocks API."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from pymice import check_blocks, make_blocks, mice, name_blocks

ROOT = Path(__file__).resolve().parents[2]
NHANES = ROOT / "tests" / "data" / "nhanes.csv"


def _load_nhanes() -> tuple[np.ndarray, list[str]]:
    names = ["age", "bmi", "hyp", "chl"]
    with NHANES.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    matrix = np.array(
        [[float(r[n]) if r[n] != "NA" else np.nan for n in names] for r in rows],
        dtype=np.float64,
    )
    return matrix, names


def test_make_blocks_scatter_and_collect():
    names = ["a", "b", "c"]
    scatter = make_blocks(names)
    assert scatter == {"a": ["a"], "b": ["b"], "c": ["c"]}
    collect = make_blocks(names, partition="collect")
    assert collect == {"collect": ["a", "b", "c"]}


def test_name_blocks_assigns_generated_names():
    blocks = name_blocks([["hyp", "chl"], ["age"]])
    assert blocks == {"B1": ["hyp", "chl"], "age": ["age"]}


def test_check_blocks_rejects_unknown_variables():
    try:
        check_blocks({"B1": ["missing"]}, ["a", "b"])
        raised = False
    except ValueError as exc:
        raised = True
        assert "missing" in str(exc)
    assert raised


def test_mice_runs_with_custom_blocks():
    data, names = _load_nhanes()
    blocks = name_blocks([["hyp", "chl"], ["age"], ["bmi"]])
    result = mice(
        data,
        column_names=names,
        blocks=blocks,
        method="mean",
        m=1,
        maxit=1,
        seed=1,
    )
    assert set(result.blocks.keys()) == {"B1", "age", "bmi"}
    filled = result.imp["hyp"].shape[0] > 0
    assert filled
