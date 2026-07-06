"""R ``summary.data.frame`` layouts with factor level counts."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "tests" / "data"


def _numeric_stats(col: np.ndarray) -> dict[str, float]:
    obs = col[np.isfinite(col)]
    if obs.size == 0:
        return {k: float("nan") for k in ("min", "q1", "med", "mean", "q3", "max")}
    return {
        "min": float(np.min(obs)),
        "q1": float(np.percentile(obs, 25)),
        "med": float(np.median(obs)),
        "mean": float(np.mean(obs)),
        "q3": float(np.percentile(obs, 75)),
        "max": float(np.max(obs)),
    }


def _level_counts(col: np.ndarray, codes: tuple[int, ...]) -> dict[int, int]:
    counts = Counter(int(v) for v in col[np.isfinite(col)])
    return {code: counts.get(code, 0) for code in codes}


def format_summary_nhanes2_r(data: np.ndarray, names: list[str]) -> str:
    idx = {n: names.index(n) for n in names}
    age = _level_counts(data[:, idx["age"]], (1, 2, 3))
    hyp = _level_counts(data[:, idx["hyp"]], (1, 2))
    bmi = _numeric_stats(data[:, idx["bmi"]])
    chl = _numeric_stats(data[:, idx["chl"]])
    n_bmi = int(np.sum(~np.isfinite(data[:, idx["bmi"]])))
    n_hyp = int(np.sum(~np.isfinite(data[:, idx["hyp"]])))
    n_chl = int(np.sum(~np.isfinite(data[:, idx["chl"]])))
    return "\n".join(
        [
            "    age          bmi          hyp          chl",
            f" 20-39:{age[1]:2d}   Min.   :{bmi['min']:4.2f}   no  :{hyp[1]:2d}   Min.   :{chl['min']:4.1f}",
            f" 40-59:{age[2]:2d}   1st Qu.:{bmi['q1']:4.2f}   yes :{hyp[2]:2d}   1st Qu.:{chl['q1']:4.1f}",
            f" 60-99:{age[3]:2d}   Median :{bmi['med']:4.2f}   NA's:{n_hyp:2d}   Median :{chl['med']:4.1f}",
            f"            Mean   :{bmi['mean']:4.2f}             Mean   :{chl['mean']:4.1f}",
            f"            3rd Qu.:{bmi['q3']:4.2f}             3rd Qu.:{chl['q3']:4.1f}",
            f"            Max.   :{bmi['max']:4.2f}             Max.   :{chl['max']:4.1f}",
            f"            NA's   :{n_bmi:2d}                 NA's   :{n_chl:2d}",
        ]
    )


def format_summary_boys_r(
    data: np.ndarray,
    names: list[str],
    *,
    compact_factors: bool = False,
) -> str:
    idx = {n: names.index(n) for n in names}
    stats = {n: _numeric_stats(data[:, idx[n]]) for n in ("age", "hgt", "wgt", "bmi", "hc", "tv")}
    gen = _level_counts(data[:, idx["gen"]], tuple(range(1, 7)))
    phb = _level_counts(data[:, idx["phb"]], tuple(range(1, 7)))
    reg = _level_counts(data[:, idx["reg"]], tuple(range(1, 6)))
    n_hgt = int(np.sum(~np.isfinite(data[:, idx["hgt"]])))
    n_wgt = int(np.sum(~np.isfinite(data[:, idx["wgt"]])))
    n_bmi = int(np.sum(~np.isfinite(data[:, idx["bmi"]])))
    n_hc = int(np.sum(~np.isfinite(data[:, idx["hc"]])))
    n_gen = int(np.sum(~np.isfinite(data[:, idx["gen"]])))
    n_phb = int(np.sum(~np.isfinite(data[:, idx["phb"]])))
    n_tv = int(np.sum(~np.isfinite(data[:, idx["tv"]])))
    n_reg = int(np.sum(~np.isfinite(data[:, idx["reg"]])))

    lines = [
        "      age              hgt              wgt              bmi",
        (
            f" Min.   : {stats['age']['min']:5.3f}   Min.   : {stats['hgt']['min']:6.2f}   "
            f"Min.   : {stats['wgt']['min']:6.2f}   Min.   :{stats['bmi']['min']:5.2f}"
        ),
        (
            f" 1st Qu.: {stats['age']['q1']:5.3f}   1st Qu.: {stats['hgt']['q1']:6.2f}   "
            f"1st Qu.: {stats['wgt']['q1']:6.2f}   1st Qu.:{stats['bmi']['q1']:5.2f}"
        ),
        (
            f" Median : {stats['age']['med']:5.3f}   Median : {stats['hgt']['med']:6.2f}   "
            f"Median : {stats['wgt']['med']:6.2f}   Median :{stats['bmi']['med']:5.2f}"
        ),
        (
            f" Mean   : {stats['age']['mean']:5.3f}   Mean   : {stats['hgt']['mean']:6.2f}   "
            f"Mean   : {stats['wgt']['mean']:6.2f}   Mean   :{stats['bmi']['mean']:5.2f}"
        ),
        (
            f" 3rd Qu.: {stats['age']['q3']:5.3f}   3rd Qu.: {stats['hgt']['q3']:6.2f}   "
            f"3rd Qu.: {stats['wgt']['q3']:6.2f}   3rd Qu.:{stats['bmi']['q3']:5.2f}"
        ),
        (
            f" Max.   : {stats['age']['max']:5.3f}   Max.   : {stats['hgt']['max']:6.2f}   "
            f"Max.   : {stats['wgt']['max']:6.2f}   Max.   :{stats['bmi']['max']:5.2f}"
        ),
    ]
    if not compact_factors:
        lines.append(
            f"                  NA's   :{n_hgt:2d}       NA's   :{n_wgt:2d}        NA's   :{n_bmi:2d}"
        )

    if compact_factors:
        lines[0] = "age              hgt              wgt              bmi"
        lines.extend(
            [
                "       hc        gen      phb            tv            reg",
                (
                    f" Min.   :{stats['hc']['min']:5.2f}   G1:{gen[1]:3d}   P1:{phb[1]:3d}   "
                    f"Min.   : {stats['tv']['min']:6.3f}   north:{reg[1]:3d}"
                ),
                (
                    f" 1st Qu.:{stats['hc']['q1']:5.2f}   G2:{gen[2]:3d}   P2:{phb[2]:3d}   "
                    f"1st Qu.: {stats['tv']['q1']:6.3f}   east :{reg[2]:3d}"
                ),
                (
                    f" Median :{stats['hc']['med']:5.2f}   G3:{gen[3]:3d}   P3:{phb[3]:3d}   "
                    f"Median : {stats['tv']['med']:6.3f}   west :{reg[3]:3d}"
                ),
                (
                    f" Mean   :{stats['hc']['mean']:5.2f}   G4:{gen[4]:3d}   P4:{phb[4]:3d}   "
                    f"Mean   : {stats['tv']['mean']:7.3f}   south:{reg[4]:3d}"
                ),
                (
                    f" 3rd Qu.:{stats['hc']['q3']:5.2f}   G5:{gen[5]:3d}   P5:{phb[5]:3d}   "
                    f"3rd Qu.: {stats['tv']['q3']:6.3f}   city :{reg[5]:3d}"
                ),
                (
                    f" Max.   :{stats['hc']['max']:5.2f}             P6:{phb[6]:3d}   "
                    f"Max.   : {stats['tv']['max']:6.3f}"
                ),
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            "       hc          gen        phb            tv           reg",
            (
                f" Min.   :{stats['hc']['min']:5.2f}   G1  : {gen[1]:3d}   P1  : {phb[1]:3d}   "
                f"Min.   : {stats['tv']['min']:5.2f}   north: {reg[1]:3d}"
            ),
            (
                f" 1st Qu.:{stats['hc']['q1']:5.2f}   G2  : {gen[2]:3d}   P2  : {phb[2]:3d}   "
                f"1st Qu.: {stats['tv']['q1']:5.2f}   east :{reg[2]:3d}"
            ),
            (
                f" Median :{stats['hc']['med']:5.2f}   G3  : {gen[3]:3d}   P3  : {phb[3]:3d}   "
                f"Median :{stats['tv']['med']:5.2f}   west :{reg[3]:3d}"
            ),
            (
                f" Mean   :{stats['hc']['mean']:5.2f}   G4  : {gen[4]:3d}   P4  : {phb[4]:3d}   "
                f"Mean   :{stats['tv']['mean']:5.2f}   south:{reg[4]:3d}"
            ),
            (
                f" 3rd Qu.:{stats['hc']['q3']:5.2f}   G5  : {gen[5]:3d}   P5  : {phb[5]:3d}   "
                f"3rd Qu.: {stats['tv']['q3']:5.2f}   city :{reg[5]:3d}"
            ),
            (
                f" Max.   :{stats['hc']['max']:5.2f}   NA's:{n_gen:3d}   P6  : {phb[6]:3d}   "
                f"Max.   :{stats['tv']['max']:5.2f}   NA's : {n_reg:3d}"
            ),
            f" NA's   :{n_hc:2d}                 NA's:{n_phb:3d}   NA's   :{n_tv:3d}",
        ]
    )
    return "\n".join(lines)


def format_summary_mammalsleep_r(data: np.ndarray, names: list[str]) -> str:
    idx = {n: names.index(n) for n in names}
    stats = {n: _numeric_stats(data[:, idx[n]]) for n in names if n != "species"}

    path = DATA / "mammalsleep.csv"
    with path.open(newline="") as fh:
        species = [row["species"] for row in csv.DictReader(fh)]
    counts = Counter(species)
    ordered = sorted(counts.keys())
    shown = ordered[:6]

    def _bw(label: str, key: str) -> str:
        return f"{label:7}:{stats['bw'][key]:8.3f}"

    def _brw(label: str, key: str) -> str:
        return f"{label:7}:{stats['brw'][key]:7.2f}"

    lines = ["                      species         bw                brw"]
    stat_keys = ("min", "q1", "med", "mean", "q3", "max")
    stat_labels = ("Min.", "1st Qu.", "Median", "Mean", "3rd Qu.", "Max.")
    for sp, label, key in zip(shown, stat_labels, stat_keys, strict=True):
        pad = " " * (25 - len(sp))
        lines.append(f" {sp}{pad}: 1   {_bw(label, key)}   {_brw(label, key)}")
    lines.append(" (Other)                  :56")

    lines.append("      sws               ps              ts             mls")
    lines.extend(
        [
            (
                f" Min.   : {stats['sws']['min']:5.3f}   Min.   :{stats['ps']['min']:5.3f}   "
                f"Min.   : {stats['ts']['min']:5.2f}   Min.   : {stats['mls']['min']:7.3f}"
            ),
            (
                f" 1st Qu.: {stats['sws']['q1']:5.3f}   1st Qu.:{stats['ps']['q1']:5.3f}   "
                f"1st Qu.: {stats['ts']['q1']:5.2f}   1st Qu.: {stats['mls']['q1']:7.3f}"
            ),
            (
                f" Median : {stats['sws']['med']:5.3f}   Median :{stats['ps']['med']:5.3f}   "
                f"Median :{stats['ts']['med']:5.2f}   Median : {stats['mls']['med']:7.3f}"
            ),
            (
                f" Mean   : {stats['sws']['mean']:5.3f}   Mean   :{stats['ps']['mean']:5.3f}   "
                f"Mean   :{stats['ts']['mean']:5.2f}   Mean   : {stats['mls']['mean']:7.3f}"
            ),
            (
                f" 3rd Qu.: {stats['sws']['q3']:5.3f}   3rd Qu.:{stats['ps']['q3']:5.3f}   "
                f"3rd Qu.: {stats['ts']['q3']:5.2f}   3rd Qu.: {stats['mls']['q3']:7.3f}"
            ),
            (
                f" Max.   : {stats['sws']['max']:5.3f}   Max.   :{stats['ps']['max']:5.3f}   "
                f"Max.   : {stats['ts']['max']:5.2f}   Max.   : {stats['mls']['max']:7.3f}"
            ),
        ]
    )
    n_sws = int(np.sum(~np.isfinite(data[:, idx["sws"]])))
    n_ps = int(np.sum(~np.isfinite(data[:, idx["ps"]])))
    n_ts = int(np.sum(~np.isfinite(data[:, idx["ts"]])))
    n_mls = int(np.sum(~np.isfinite(data[:, idx["mls"]])))
    lines.append(
        f" NA's   :{n_sws:2d}       NA's   :{n_ps:2d}      NA's   :{n_ts:2d}       NA's   :{n_mls:2d}"
    )

    lines.append("       gt               pi             sei             odi")
    lines.extend(
        [
            (
                f" Min.   : {stats['gt']['min']:6.2f}   Min.   :{stats['pi']['min']:6.3f}   "
                f"Min.   :{stats['sei']['min']:6.3f}   Min.   :{stats['odi']['min']:6.3f}"
            ),
            (
                f" 1st Qu.: {stats['gt']['q1']:6.2f}   1st Qu.:{stats['pi']['q1']:6.3f}   "
                f"1st Qu.:{stats['sei']['q1']:6.3f}   1st Qu.:{stats['odi']['q1']:6.3f}"
            ),
            (
                f" Median : {stats['gt']['med']:6.2f}   Median :{stats['pi']['med']:6.3f}   "
                f"Median :{stats['sei']['med']:6.3f}   Median :{stats['odi']['med']:6.3f}"
            ),
            (
                f" Mean   : {stats['gt']['mean']:7.2f}   Mean   :{stats['pi']['mean']:6.3f}   "
                f"Mean   :{stats['sei']['mean']:6.3f}   Mean   :{stats['odi']['mean']:6.3f}"
            ),
            (
                f" 3rd Qu.: {stats['gt']['q3']:6.2f}   3rd Qu.:{stats['pi']['q3']:6.3f}   "
                f"3rd Qu.:{stats['sei']['q3']:6.3f}   3rd Qu.:{stats['odi']['q3']:6.3f}"
            ),
            (
                f" Max.   : {stats['gt']['max']:6.2f}   Max.   :{stats['pi']['max']:6.3f}   "
                f"Max.   :{stats['sei']['max']:6.3f}   Max.   :{stats['odi']['max']:6.3f}"
            ),
        ]
    )
    n_gt = int(np.sum(~np.isfinite(data[:, idx["gt"]])))
    lines.append(f" NA's   :{n_gt:2d}")
    return "\n".join(lines)


BOYS_HEAD_ROW_NAMES = (3, 4, 18, 23, 28, 36)


def _ms_num(name: str, raw: str) -> str:
    if raw in ("", "NA", None):
        return "NA"
    val = float(raw)
    if name == "bw":
        return f"{val:.3f}"
    if name == "brw":
        return f"{val:.1f}"
    if name in {"sws", "ps", "ts", "mls"}:
        return f"{val:.1f}"
    if name == "gt":
        return str(int(val)) if abs(val - round(val)) < 1e-9 else f"{val:.1f}"
    return str(int(float(raw)))


def format_mammalsleep_head_r(*, n: int = 6) -> str:
    """``head(mammalsleep)`` with species labels (R factor print)."""
    path = DATA / "mammalsleep.csv"
    with path.open(newline="") as fh:
        rows = list(csv.DictReader(fh))[:n]

    lines = ["                     species       bw    brw sws  ps   ts  mls  gt pi sei"]
    for i, row in enumerate(rows, start=1):
        lines.append(
            f"{i} {row['species']:>25} {_ms_num('bw', row['bw']):>8} {_ms_num('brw', row['brw']):>6} "
            f"{_ms_num('sws', row['sws']):>4} {_ms_num('ps', row['ps']):>3} "
            f"{_ms_num('ts', row['ts']):>4} {_ms_num('mls', row['mls']):>5} "
            f"{_ms_num('gt', row['gt']):>4} {row['pi']:>2} {row['sei']:>3}"
        )
    lines.append("  odi")
    for i, row in enumerate(rows, start=1):
        lines.append(f"{i}   {row['odi']}")
    return "\n".join(lines)


def format_boys_head_r(*, n: int = 6) -> str:
    """``head(boys)`` with R row names and factor labels."""
    path = DATA / "boys.csv"
    with path.open(newline="") as fh:
        rows = list(csv.DictReader(fh))[:n]

    def _cell(name: str, raw: str) -> str:
        if raw in ("", "NA", None):
            return "<NA>" if name in {"gen", "phb"} else "NA"
        if name == "reg":
            return raw
        val = float(raw)
        if name == "age":
            return f"{val:.3f}"
        if name == "hgt":
            return f"{val:.1f}"
        if name == "wgt":
            return f"{val:.3f}"
        if name == "bmi":
            return f"{val:.2f}"
        if name == "hc":
            return f"{val:.1f}"
        return raw

    lines = ["     age  hgt   wgt   bmi   hc  gen  phb tv   reg"]
    for row_name, row in zip(BOYS_HEAD_ROW_NAMES, rows, strict=True):
        row_prefix = f"{row_name}  " if row_name < 10 else f"{row_name} "
        lines.append(
            f"{row_prefix}{_cell('age', row['age'])} {_cell('hgt', row['hgt'])} "
            f"{_cell('wgt', row['wgt'])} {_cell('bmi', row['bmi'])} "
            f"{_cell('hc', row['hc'])} {_cell('gen', row['gen'])} "
            f"{_cell('phb', row['phb'])} {_cell('tv', row['tv'])} {_cell('reg', row['reg'])}"
        )
    return "\n".join(lines)


def _popncr_stats(col: np.ndarray) -> dict[str, float]:
    obs = col[np.isfinite(col)]
    if obs.size == 0:
        return {k: float("nan") for k in ("min", "q1", "med", "mean", "q3", "max")}
    return {
        "min": float(np.min(obs)),
        "q1": float(np.percentile(obs, 25)),
        "med": float(np.median(obs)),
        "mean": float(np.mean(obs)),
        "q3": float(np.percentile(obs, 75)),
        "max": float(np.max(obs)),
    }


def format_popncr_head_r(data: np.ndarray, names: list[str], *, n: int = 15) -> str:
    """``head(complete(imp2, 1), n=15)`` layout from the multilevel vignette."""
    cols = ["pupil", "class", "extrav", "sex", "texp", "popular", "popteach"]
    idx = {c: names.index(c) for c in cols}
    lines = ["   pupil class   extrav sex texp  popular popteach"]

    def _int_cell(value: float, width: int) -> str:
        if np.isfinite(value) and abs(value - round(value)) < 1e-9:
            return str(round(value)).rjust(width)
        return f"{value:.0f}".rjust(width)

    for i in range(min(n, data.shape[0])):
        row = data[i]
        rn = i + 1
        gap = 6 if rn < 10 else 4
        lines.append(
            f"{rn}{' ' * gap}"
            f"{_int_cell(row[idx['pupil']], 7)}"
            f"{_int_cell(row[idx['class']], 6)}"
            f"{row[idx['extrav']]:9.6f}"
            f"{_int_cell(row[idx['sex']], 4)}"
            f"{_int_cell(row[idx['texp']], 5)}"
            f"{row[idx['popular']]:9.6f}"
            f"{row[idx['popteach']]:9.6f}"
        )
    return "\n".join(lines)


def format_summary_popncr_r(data: np.ndarray, names: list[str], *, imputed: bool = False) -> str:
    """R ``summary(popNCR)`` / ``summary(complete(imp))`` (factor ``class`` layout)."""
    idx = {n: names.index(n) for n in names}
    cls = data[:, idx["class"]]
    cls_obs = cls[np.isfinite(cls)].astype(int)
    top_cls = [lvl for lvl, _ in Counter(cls_obs).most_common(6)]
    other_cls = int(cls_obs.size - sum(Counter(cls_obs)[lvl] for lvl in top_cls))

    sex = data[:, idx["sex"]]
    n0 = int(np.sum(sex == 0))
    n1 = int(np.sum(sex == 1))
    n_sex_na = int(np.sum(~np.isfinite(sex)))

    s_pupil = _popncr_stats(data[:, idx["pupil"]])
    s_extrav = _popncr_stats(data[:, idx["extrav"]])
    s_texp = _popncr_stats(data[:, idx["texp"]])
    s_pop = _popncr_stats(data[:, idx["popular"]])
    s_pt = _popncr_stats(data[:, idx["popteach"]])

    if imputed:
        lines = ["     pupil           class          extrav        sex           texp       "]
        stat_rows = [
            ("Min.", s_pupil, s_extrav, s_texp, ("0", n0), False),
            ("1st Qu.", s_pupil, s_extrav, s_texp, ("1", n1), False),
            ("Median", s_pupil, s_extrav, s_texp, None, True),
            ("Mean", s_pupil, s_extrav, s_texp, None, True),
            ("3rd Qu.", s_pupil, s_extrav, s_texp, None, True),
            ("Max.", s_pupil, s_extrav, s_texp, None, True),
        ]
        key_map = {
            "Min.": "min",
            "1st Qu.": "q1",
            "Median": "med",
            "Mean": "mean",
            "3rd Qu.": "q3",
            "Max.": "max",
        }
        for i, (lab, sp, se, st, sex_info, skip_sex) in enumerate(stat_rows):
            k = key_map[lab]
            pupil = (
                f" Min.   : {sp[k]:5.2f}"
                if lab == "Min."
                else (
                    f" 1st Qu.: {sp[k]:5.2f}"
                    if lab == "1st Qu."
                    else f" Median :{sp[k]:6.2f}"
                    if lab == "Median"
                    else f" Mean   :{sp[k]:6.2f}"
                    if lab == "Mean"
                    else f" 3rd Qu.:{sp[k]:6.2f}"
                    if lab == "3rd Qu."
                    else f" Max.   :{sp[k]:6.2f}"
                )
            )
            cls_cnt = Counter(cls_obs)[top_cls[i]]
            cls_part = f"   {top_cls[i]:5d}     : {cls_cnt:3d}   "
            if lab == "Min.":
                extrav = f"Min.   : {se[k]:7.4f}"
            elif lab == "1st Qu.":
                extrav = f"1st Qu.: {se[k]:7.4f}"
            elif lab == "Median":
                extrav = f"Median : {se[k]:7.4f}"
            elif lab == "Mean":
                extrav = f"Mean   : {se[k]:7.4f}"
            elif lab == "3rd Qu.":
                extrav = f"3rd Qu.: {se[k]:7.4f}"
            else:
                extrav = f"Max.   :{se[k]:8.4f}"
            if sex_info:
                sex_part = f"   {sex_info[0]}: {sex_info[1]:3d}   "
            elif skip_sex:
                sex_part = "                 "
            else:
                sex_part = "                 "
            if lab == "Min.":
                texp = f"Min.   :{st[k]:7.3f}"
            elif lab == "1st Qu.":
                texp = f"1st Qu.: {st[k]:6.3f}"
            elif lab == "Median":
                texp = f"Median :{st[k]:7.3f}"
            elif lab == "Mean":
                texp = f"Mean   :{st[k]:7.3f}"
            elif lab == "3rd Qu.":
                texp = f"3rd Qu.:{st[k]:7.3f}"
            else:
                texp = f"Max.   :{st[k]:7.3f}"
            lines.append(f"{pupil}{cls_part}{extrav}{sex_part}{texp}".rstrip())
        lines.append(
            f"                 (Other):{other_cls:4d}                                              "
        )
        lines.append("    popular         popteach    ")
        pop_labels = [
            (f" Min.   :{s_pop['min']:5.3f}", f" Min.   : {s_pt['min']:5.2f}"),
            (f" 1st Qu.:{s_pop['q1']:5.3f}", f" 1st Qu.: {s_pt['q1']:5.2f}"),
            (f" Median :{s_pop['med']:5.3f}", f" Median : {s_pt['med']:5.2f}"),
            (f" Mean   :{s_pop['mean']:5.3f}", f" Mean   : {s_pt['mean']:5.2f}"),
            (f" 3rd Qu.:{s_pop['q3']:5.3f}", f" 3rd Qu.: {s_pt['q3']:5.2f}"),
            (f" Max.   :{s_pop['max']:5.3f}", f" Max.   :{s_pt['max']:5.2f}"),
        ]
        for pop, pt in pop_labels:
            lines.append(f"{pop}   {pt}")
        return "\n".join(lines)

    lines = ["pupil           class          extrav         sex           texp"]
    rows = [
        ("min", f" Min.   : {s_pupil['min']:4.2f}"),
        ("q1", f" 1st Qu.: {s_pupil['q1']:4.2f}"),
        ("med", f" Median :{s_pupil['med']:5.2f}"),
        ("mean", f" Mean   :{s_pupil['mean']:5.2f}"),
        ("q3", f" 3rd Qu.:{s_pupil['q3']:5.2f}"),
        ("max", f" Max.   :{s_pupil['max']:5.2f}"),
    ]
    for i, (key, pupil_part) in enumerate(rows):
        cls_cnt = Counter(cls_obs)[top_cls[i]]
        cls_part = f"   {top_cls[i]:5d}     : {cls_cnt:3d}   "
        if key == "min":
            extrav = f"   Min.   : {s_extrav[key]:5.3f}"
        elif key == "q1":
            extrav = f"   1st Qu.: {s_extrav[key]:5.3f}"
        elif key == "med":
            extrav = f"   Median : {s_extrav[key]:5.3f}"
        elif key == "mean":
            extrav = f"   Mean   : {s_extrav[key]:5.3f}"
        elif key == "q3":
            extrav = f"   3rd Qu.: {s_extrav[key]:5.3f}"
        else:
            extrav = f"   Max.   :{s_extrav[key]:6.3f}"
        if i == 0:
            sex_part = f"   0   :{n0:3d}   "
        elif i == 1:
            sex_part = f"   1   :{n1:3d}   "
        elif i == 2:
            sex_part = f"   NA's:{n_sex_na:3d}   "
        else:
            sex_part = "                 "
        if key == "min":
            texp = f"   Min.   : {s_texp[key]:4.1f}"
        elif key == "q1":
            texp = f"   1st Qu.: {s_texp[key]:4.1f}"
        elif key == "med":
            texp = f"   Median :{s_texp[key]:5.1f}"
        elif key == "mean":
            texp = f"   Mean   :{s_texp[key]:5.1f}"
        elif key == "q3":
            texp = f"   3rd Qu.:{s_texp[key]:5.1f}"
        else:
            texp = f"   Max.   :{s_texp[key]:5.1f}"
        lines.append(f"{pupil_part}{cls_part}{extrav}{sex_part}{texp}".rstrip())

    lines.append(
        f"                 (Other):{other_cls:4d}"
        f"   NA's   :{int(np.sum(~np.isfinite(data[:, idx['extrav']]))):4d}"
        f"                 NA's   :{int(np.sum(~np.isfinite(data[:, idx['texp']]))):4d}"
    )
    lines.append("    popular         popteach     ")
    pop_rows = [
        (f" Min.   :{s_pop['min']:5.3f}", f" Min.   : {s_pt['min']:5.3f}"),
        (f" 1st Qu.:{s_pop['q1']:5.3f}", f" 1st Qu.: {s_pt['q1']:5.3f}"),
        (f" Median :{s_pop['med']:5.3f}", f" Median : {s_pt['med']:5.3f}"),
        (f" Mean   :{s_pop['mean']:5.3f}", f" Mean   : {s_pt['mean']:5.3f}"),
        (f" 3rd Qu.:{s_pop['q3']:5.3f}", f" 3rd Qu.: {s_pt['q3']:5.3f}"),
        (f" Max.   :{s_pop['max']:5.3f}", f" Max.   :{s_pt['max']:5.3f}"),
    ]
    for pop, pt in pop_rows:
        lines.append(f"{pop}   {pt}")
    lines.append(
        f"{'':14}NA's   :{int(np.sum(~np.isfinite(data[:, idx['popular']]))):3d}"
        f"     NA's   :{int(np.sum(~np.isfinite(data[:, idx['popteach']]))):3d}"
    )
    return "\n".join(lines)
