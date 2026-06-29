"""Bundled tutorial datasets (``pymice.datasets.load_*``)."""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from pymice.types import VariableKind, VariableSpec


def _data_root() -> Path:
    here = Path(__file__).resolve().parent
    bundled = here / "data"
    if bundled.is_dir():
        return bundled
    return here.parent.parent / "tests" / "data"


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"empty csv: {path}")
    return list(rows[0].keys()), rows


def _load_numeric(
    path: Path, names: list[str] | None = None
) -> tuple[NDArray[np.float64], list[str]]:
    colnames, rows = _read_csv(path)
    use = names or colnames
    matrix = np.array(
        [[float(r[n]) if r.get(n, "NA") not in ("", "NA") else np.nan for n in use] for r in rows],
        dtype=np.float64,
    )
    return matrix, use


@lru_cache(maxsize=1)
def load_nhanes() -> tuple[NDArray[np.float64], list[str]]:
    return _load_numeric(_data_root() / "nhanes.csv", ["age", "bmi", "hyp", "chl"])


@lru_cache(maxsize=1)
def load_nhanes2() -> tuple[NDArray[np.float64], list[str], list[VariableSpec]]:
    path = _data_root() / "nhanes2.csv"
    age_map = {"20-39": 1.0, "40-59": 2.0, "60-99": 3.0}
    hyp_map = {"no": 1.0, "yes": 2.0}
    _, rows = _read_csv(path)
    matrix = np.array(
        [
            [
                age_map.get(r["age"].strip().strip('"'), np.nan),
                float(r["bmi"]),
                hyp_map.get(r["hyp"].strip().strip('"'), np.nan),
                float(r["chl"]),
            ]
            for r in rows
        ],
        dtype=np.float64,
    )
    names = ["age", "bmi", "hyp", "chl"]
    specs = [
        VariableSpec("age", VariableKind.UNORDERED, levels=(1.0, 2.0, 3.0)),
        VariableSpec("bmi", VariableKind.NUMERIC),
        VariableSpec("hyp", VariableKind.BINARY, levels=(1.0, 2.0)),
        VariableSpec("chl", VariableKind.NUMERIC),
    ]
    return matrix, names, specs


@lru_cache(maxsize=1)
def load_boys() -> tuple[NDArray[np.float64], list[str]]:
    names = ["age", "hgt", "wgt", "bmi", "hc", "gen", "phb", "tv", "reg"]
    return _load_numeric(_data_root() / "boys.csv", names)


@lru_cache(maxsize=1)
def load_mammalsleep(*, include_species: bool = True) -> tuple[NDArray[np.float64], list[str]]:
    path = _data_root() / "mammalsleep.csv"
    colnames, rows = _read_csv(path)
    if include_species:
        names = list(colnames)
        matrix = np.array(
            [
                [
                    float(i + 1)
                    if n == "species"
                    else float(r[n])
                    if r.get(n, "NA") not in ("", "NA")
                    else np.nan
                    for n in names
                ]
                for i, r in enumerate(rows)
            ],
            dtype=np.float64,
        )
        return matrix, names
    names = [c for c in colnames if c != "species"]
    matrix = np.array(
        [
            [float(r[n]) if r.get(n, "NA") not in ("", "NA") else np.nan for n in names]
            for r in rows
        ],
        dtype=np.float64,
    )
    return matrix, names


@lru_cache(maxsize=1)
def load_leiden() -> tuple[NDArray[np.float64], list[str]]:
    names = ["sexe", "lftanam", "rrsyst", "rrdiast", "dwa", "survda", "alb", "chol", "mmse", "woon"]
    return _load_numeric(_data_root() / "leiden.csv", names)


@lru_cache(maxsize=1)
def load_popncr() -> tuple[NDArray[np.float64], list[str]]:
    names = ["pupil", "class", "extrav", "sex", "texp", "popular", "popteach"]
    return _load_numeric(_data_root() / "popNCR.csv", names)


@lru_cache(maxsize=1)
def load_popncr2() -> tuple[NDArray[np.float64], list[str]]:
    names = ["pupil", "class", "extrav", "sex", "texp", "popular", "popteach"]
    return _load_numeric(_data_root() / "popNCR2.csv", names)


@lru_cache(maxsize=1)
def load_popncr3() -> tuple[NDArray[np.float64], list[str]]:
    names = ["pupil", "class", "extrav", "sex", "texp", "popular", "popteach"]
    return _load_numeric(_data_root() / "popNCR3.csv", names)
