"""Data loading helpers for vignette commands."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "tests" / "data"


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"empty csv: {path}")
    return list(rows[0].keys()), rows


def load_csv_numeric(path: Path, names: list[str] | None = None) -> tuple[np.ndarray, list[str]]:
    colnames, rows = _read_csv(path)
    use = names or colnames
    matrix = np.array(
        [[float(r[n]) if r.get(n, "NA") not in ("", "NA") else np.nan for n in use] for r in rows],
        dtype=np.float64,
    )
    return matrix, use


def load_ampute_testdata() -> tuple[np.ndarray, list[str]]:
    """Bundled V07 ``testdata`` (R ``MASS::mvrnorm``, seed 2016)."""
    names = ["V1", "V2", "V3"]
    return load_csv_numeric(DATA / "ampute_testdata.csv", names)


def load_nhanes() -> tuple[np.ndarray, list[str]]:
    names = ["age", "bmi", "hyp", "chl"]
    return load_csv_numeric(DATA / "nhanes.csv", names)


def _to_float(val: str) -> float:
    val = val.strip().strip('"')
    if val in ("", "NA"):
        return np.nan
    return float(val)


def load_nhanes2() -> tuple[np.ndarray, list[str]]:
    """Factor-coded nhanes2: age 1-3, hyp 1-2 (same coding as tests)."""
    names = ["age", "bmi", "hyp", "chl"]
    path = DATA / "nhanes2.csv"
    age_map = {"20-39": 1.0, "40-59": 2.0, "60-99": 3.0}
    hyp_map = {"no": 1.0, "yes": 2.0}
    _, rows = _read_csv(path)

    def _code_age(val: str) -> float:
        v = val.strip().strip('"')
        if v in ("", "NA"):
            return np.nan
        if v in age_map:
            return age_map[v]
        return _to_float(v)

    def _code_hyp(val: str) -> float:
        v = val.strip().strip('"')
        if v in ("", "NA"):
            return np.nan
        if v in hyp_map:
            return hyp_map[v]
        return _to_float(v)

    matrix = np.array(
        [
            [
                _code_age(r["age"]),
                _to_float(r["bmi"]),
                _code_hyp(r["hyp"]),
                _to_float(r["chl"]),
            ]
            for r in rows
        ],
        dtype=np.float64,
    )
    return matrix, names


def load_boys_numeric() -> tuple[np.ndarray, list[str]]:
    """Boys growth data — numeric columns for md.pattern parity."""
    names = ["age", "hgt", "wgt", "bmi", "hc", "tv"]
    return load_csv_numeric(DATA / "boys.csv", names)


def load_boys_full_matrix() -> tuple[np.ndarray, list[str]]:
    """All boys columns with factor columns encoded as numeric + NA."""
    _colnames, rows = _read_csv(DATA / "boys.csv")
    names = ["age", "reg", "wgt", "hgt", "bmi", "hc", "gen", "phb", "tv"]
    reg_map = {"north": 1, "east": 2, "west": 3, "south": 4, "city": 5}
    gen_map = {f"G{i}": i for i in range(1, 6)}
    phb_map = {f"P{i}": i for i in range(1, 7)}

    def code(val: str, mapping: dict[str, int]) -> float:
        if val in ("", "NA") or val is None:
            return np.nan
        if val in mapping:
            return float(mapping[val])
        return float(val) if val.replace(".", "", 1).isdigit() else np.nan

    matrix = np.array(
        [
            [
                float(r["age"]) if r["age"] not in ("", "NA") else np.nan,
                code(r.get("reg", "NA"), reg_map),
                float(r["wgt"]) if r["wgt"] not in ("", "NA") else np.nan,
                float(r["hgt"]) if r["hgt"] not in ("", "NA") else np.nan,
                float(r["bmi"]) if r["bmi"] not in ("", "NA") else np.nan,
                float(r["hc"]) if r["hc"] not in ("", "NA") else np.nan,
                code(r.get("gen", "NA"), gen_map),
                code(r.get("phb", "NA"), phb_map),
                float(r["tv"]) if r["tv"] not in ("", "NA") else np.nan,
            ]
            for r in rows
        ],
        dtype=np.float64,
    )
    return matrix, names


def load_boys_impute() -> tuple[np.ndarray, list[str]]:
    """Boys in R ``mice`` column order (vignettes 03–04 imputation)."""
    names = ["age", "hgt", "wgt", "bmi", "hc", "gen", "phb", "tv", "reg"]
    _colnames, rows = _read_csv(DATA / "boys.csv")
    reg_map = {"north": 1, "east": 2, "west": 3, "south": 4, "city": 5}
    gen_map = {f"G{i}": i for i in range(1, 6)}
    phb_map = {f"P{i}": i for i in range(1, 7)}

    def code(val: str, mapping: dict[str, int]) -> float:
        if val in ("", "NA") or val is None:
            return np.nan
        if val in mapping:
            return float(mapping[val])
        return float(val) if val.replace(".", "", 1).isdigit() else np.nan

    matrix = np.array(
        [
            [
                float(r["age"]) if r["age"] not in ("", "NA") else np.nan,
                float(r["hgt"]) if r["hgt"] not in ("", "NA") else np.nan,
                float(r["wgt"]) if r["wgt"] not in ("", "NA") else np.nan,
                float(r["bmi"]) if r["bmi"] not in ("", "NA") else np.nan,
                float(r["hc"]) if r["hc"] not in ("", "NA") else np.nan,
                code(r.get("gen", "NA"), gen_map),
                code(r.get("phb", "NA"), phb_map),
                float(r["tv"]) if r["tv"] not in ("", "NA") else np.nan,
                code(r.get("reg", "NA"), reg_map),
            ]
            for r in rows
        ],
        dtype=np.float64,
    )
    return matrix, names


def load_mammalsleep_full() -> tuple[np.ndarray, list[str]]:
    """Mammalsleep with species encoded as 1..n (always observed)."""
    colnames, rows = _read_csv(DATA / "mammalsleep.csv")
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


def with_log10_bw(data: np.ndarray, names: list[str]) -> tuple[np.ndarray, list[str]]:
    """Append ``log10_bw`` column (PyMICE ``lm`` does not parse ``log10(bw)``)."""
    bw_i = names.index("bw")
    ext = np.column_stack([data, np.log10(np.maximum(data[:, bw_i], 1e-6))])
    return ext, [*names, "log10_bw"]


def load_mammalsleep_impute() -> tuple[np.ndarray, list[str]]:
    """Mammalsleep without species column (vignette 04)."""
    colnames, rows = _read_csv(DATA / "mammalsleep.csv")
    names = [c for c in colnames if c != "species"]
    matrix = np.array(
        [
            [float(r[n]) if r.get(n, "NA") not in ("", "NA") else np.nan for n in names]
            for r in rows
        ],
        dtype=np.float64,
    )
    return matrix, names


def load_leiden() -> tuple[np.ndarray, list[str]]:
    names = ["sexe", "lftanam", "rrsyst", "rrdiast", "dwa", "survda", "alb", "chol", "mmse", "woon"]
    return load_csv_numeric(DATA / "leiden.csv", names)


def popncr_variable_specs(data: np.ndarray, names: list[str]) -> list:
    """Variable kinds for popNCR* (R ``class`` factor + binary ``sex``)."""
    from pymice.types import VariableKind, VariableSpec

    class_vals = data[:, names.index("class")]
    class_levels = tuple(float(v) for v in np.unique(class_vals[~np.isnan(class_vals)]))
    specs: list[VariableSpec] = []
    for name in names:
        if name == "class":
            specs.append(VariableSpec("class", VariableKind.UNORDERED, levels=class_levels))
        elif name == "sex":
            specs.append(VariableSpec("sex", VariableKind.BINARY, levels=(0.0, 1.0)))
        else:
            specs.append(VariableSpec(name, VariableKind.NUMERIC))
    return specs


def load_popncr() -> tuple[np.ndarray, list[str]]:
    names = ["pupil", "class", "extrav", "sex", "texp", "popular", "popteach"]
    return load_csv_numeric(DATA / "popNCR.csv", names)


def load_popncr2() -> tuple[np.ndarray, list[str]]:
    names = ["pupil", "class", "extrav", "sex", "texp", "popular", "popteach"]
    return load_csv_numeric(DATA / "popNCR2.csv", names)


def load_popncr3() -> tuple[np.ndarray, list[str]]:
    names = ["pupil", "class", "extrav", "sex", "texp", "popular", "popteach"]
    return load_csv_numeric(DATA / "popNCR3.csv", names)


def load_popular() -> tuple[np.ndarray, list[str]]:
    """Complete popularity reference data (R workspace object ``popular``)."""
    names = ["pupil", "class", "extrav", "sex", "texp", "popular", "popteach"]
    return load_csv_numeric(DATA / "popular.csv", names)


def load_popular_truth() -> np.ndarray:
    """Complete `popular` reference values (R workspace object `popular`)."""
    data, names = load_popular()
    return data[:, names.index("popular")]
