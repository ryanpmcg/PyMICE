"""Bundled tutorial datasets (``data()`` and ``load_*``)."""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from pymice.types import VariableKind, VariableSpec

_DATASET_NAMES = (
    "nhanes",
    "nhanes2",
    "boys",
    "mammalsleep",
    "leiden",
    "popncr",
    "popncr2",
    "popncr3",
)


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
def _load_nhanes_cached() -> tuple[NDArray[np.float64], list[str]]:
    return _load_numeric(_data_root() / "nhanes.csv", ["age", "bmi", "hyp", "chl"])


def load_nhanes() -> tuple[NDArray[np.float64], list[str]]:
    matrix, names = _load_nhanes_cached()
    return matrix.copy(), list(names)


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


def _as_dataframe(matrix: NDArray[np.float64], names: list[str]) -> Any:
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError(
            "pandas is required for data(); install with: pip install pandas"
        ) from exc
    return pd.DataFrame(matrix, columns=names)


@lru_cache(maxsize=1)
def load_nhanes_df() -> Any:
    matrix, names = load_nhanes()
    return _as_dataframe(matrix, names)


@lru_cache(maxsize=1)
def load_nhanes2_df() -> Any:
    matrix, names, _specs = load_nhanes2()
    return _as_dataframe(matrix, names)


@lru_cache(maxsize=1)
def load_boys_df() -> Any:
    matrix, names = load_boys()
    return _as_dataframe(matrix, names)


@lru_cache(maxsize=1)
def load_mammalsleep_df(*, include_species: bool = True) -> Any:
    matrix, names = load_mammalsleep(include_species=include_species)
    return _as_dataframe(matrix, names)


@lru_cache(maxsize=1)
def load_leiden_df() -> Any:
    matrix, names = load_leiden()
    return _as_dataframe(matrix, names)


@lru_cache(maxsize=1)
def load_popncr_df() -> Any:
    matrix, names = load_popncr()
    return _as_dataframe(matrix, names)


@lru_cache(maxsize=1)
def load_popncr2_df() -> Any:
    matrix, names = load_popncr2()
    return _as_dataframe(matrix, names)


@lru_cache(maxsize=1)
def load_popncr3_df() -> Any:
    matrix, names = load_popncr3()
    return _as_dataframe(matrix, names)


def data(name: str, **kwargs: Any) -> Any:
    """
    Load a bundled dataset as a pandas DataFrame (R ``data()`` analogue).

    Available names: nhanes, nhanes2, boys, mammalsleep, leiden, popncr, popncr2, popncr3.
    """
    key = name.strip().lower()
    if key == "nhanes":
        return load_nhanes_df()
    if key == "nhanes2":
        return load_nhanes2_df()
    if key == "boys":
        return load_boys_df()
    if key == "mammalsleep":
        include_species = kwargs.get("include_species", True)
        return load_mammalsleep_df(include_species=include_species)
    if key == "leiden":
        return load_leiden_df()
    if key == "popncr":
        return load_popncr_df()
    if key == "popncr2":
        return load_popncr2_df()
    if key == "popncr3":
        return load_popncr3_df()
    known = ", ".join(_DATASET_NAMES)
    raise ValueError(f"unknown dataset {name!r}; known datasets: {known}")
