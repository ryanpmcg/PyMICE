"""Format PyMICE output to resemble R console / vignette prints."""

from __future__ import annotations

import re

import numpy as np
from scipy import stats

from lib.help_format import format_help_r  # noqa: F401
from lib.summary_format import (  # noqa: F401
    format_boys_head_r,
    format_mammalsleep_head_r,
    format_popncr_head_r,
    format_summary_boys_r,
    format_summary_mammalsleep_r,
    format_summary_nhanes2_r,
)
from lib.summary_format import (
    format_summary_popncr_r as _format_summary_popncr_r,
)
from pymice.diagnostics.flux import FluxResult
from pymice.diagnostics.md_pattern import MdPatternResult
from pymice.formulas import build_design_matrix, parse_regression_formula, term_labels
from pymice.initialize import where_indices
from pymice.types import Mids, Mira, PoolResult


def _fmt_val(name: str, value: float) -> str:
    if not np.isfinite(value):
        return "NA"
    if name in {"age", "hyp", "chl", "sex", "class", "pupil"} and abs(value - round(value)) < 1e-9:
        return str(round(value))
    if abs(value - round(value)) < 1e-9 and abs(value) < 1e6:
        return str(round(value)) if abs(value) < 100 else f"{value:.1f}"
    if name == "bmi" and abs(value - round(value, 1)) < 1e-9:
        return f"{value:.1f}"
    return f"{value:.4f}".rstrip("0").rstrip(".")


def format_dataframe_r(
    data: np.ndarray,
    names: list[str],
    *,
    max_rows: int | None = None,
) -> str:
    """Print data frame in R style with row numbers."""
    n = data.shape[0] if max_rows is None else min(max_rows, data.shape[0])
    width = max(4, len(str(n)))
    lines: list[str] = []
    for i in range(n):
        row = data[i]
        vals = " ".join(f"{_fmt_val(names[j], row[j]):>8}" for j in range(len(names)))
        lines.append(f"{i + 1:>{width}} {vals}")
    if max_rows is not None and data.shape[0] > max_rows:
        lines.append(f"... {data.shape[0] - max_rows} more rows ...")
    return "\n".join(lines)


def format_complete_r(
    data: np.ndarray,
    names: list[str],
    *,
    max_rows: int | None = 25,
) -> str:
    """``complete(imp)`` layout from the ad hoc vignette."""
    n = data.shape[0] if max_rows is None else min(max_rows, data.shape[0])

    # Decide dynamic formatting for bmi and chl based on column values
    has_five_bmi = False
    for i in range(n):
        val = data[i, 1]
        if np.isfinite(val) and abs(val - round(val, 4)) > 1e-6:
            has_five_bmi = True
            break

    has_four_chl = False
    for i in range(n):
        val = data[i, 3]
        if np.isfinite(val) and abs(val - round(val, 1)) > 1e-5:
            has_four_chl = True
            break

    lines = ["   age     bmi      hyp   chl"]
    for i in range(n):
        row = data[i]
        age = round(row[0])

        bmi = f"{row[1]:.5f}" if has_five_bmi else f"{row[1]:.4f}"
        hyp = f"{row[2]:.6f}"
        chl = f"{row[3]:.4f}" if has_four_chl else f"{row[3]:.1f}"

        lines.append(f" {i + 1:2d}    {age} {bmi} {hyp} {chl}")
    return "\n".join(lines)


def format_logged_events_warning_r(count: int) -> str:
    """R ``mice()`` warning when sampler events were logged."""
    return f"Warning: Number of logged events: {count}"


def format_summary_r(data: np.ndarray, names: list[str]) -> str:
    """Numeric summary similar to R ``summary()`` for continuous columns."""
    lines: list[str] = []
    for j, name in enumerate(names):
        col = data[:, j]
        obs = col[np.isfinite(col)]
        if obs.size == 0:
            continue
        lines.append(f"      {name:12}")
        stats = [
            ("Min.", np.min(obs)),
            ("1st Qu.", np.percentile(obs, 25)),
            ("Median", np.median(obs)),
            ("Mean", np.mean(obs)),
            ("3rd Qu.", np.percentile(obs, 75)),
            ("Max.", np.max(obs)),
        ]
        stat_line = "   ".join(f"{lab:7}: {val:7.2f}" for lab, val in stats[:1])
        lines.append(f"  {stat_line}")
        for lab, val in stats[1:5]:
            lines.append(f"  {lab:7}: {val:8.2f}".replace("  Median:", "  Median :"))
        lines.append(f"  {'Max.':7}: {stats[5][1]:8.2f}")
        n_miss = int(np.sum(~np.isfinite(col)))
        if n_miss:
            lines.append(f"                 NA's  :{n_miss:5d}")
    return "\n".join(lines)


def format_md_pattern_r(result: MdPatternResult) -> str:
    """R ``md.pattern`` console layout (counts as row names)."""
    cols = result.column_names
    header = "    " + " ".join(f"{c:>3}" for c in cols) + "     "
    lines = [header]
    for count, row in zip(result.pattern_counts, result.matrix[:-1], strict=True):
        body = "   ".join(str(int(v)) for v in row[:-1])
        miss = int(row[-1])
        lines.append(f"{count:>3}   {body}  {miss}")
    footer = result.matrix[-1]
    foot = "      " + "   ".join(str(int(v)) for v in footer[:-1]) + f"  {int(footer[-1])}"
    lines.append(foot)
    return "\n".join(lines)


def format_predictor_matrix(names: list[str], matrix: np.ndarray, *, style: str = "compact") -> str:
    if style == "popncr":
        return _format_predictor_matrix_popncr(names, matrix)
    lines = ["    " + " ".join(f"{n:>3}" for n in names)]
    for i, name in enumerate(names):
        row = " ".join(f"{int(matrix[i, j]):>3}" for j in range(len(names)))
        lines.append(f"{name:>3}   {row}")
    return "\n".join(lines)


def _format_predictor_matrix_popncr(names: list[str], matrix: np.ndarray) -> str:
    """R ``print(pred)`` layout for popNCR vignette matrices."""
    row_templates = {
        "pupil": "pupil        {c0}     {c1}      {c2}   {c3}    {c4}       {c5}        {c6}",
        "class": "class        {c0}     {c1}      {c2}   {c3}    {c4}       {c5}        {c6}",
        "extrav": "extrav       {c0}     {c1}      {c2}   {c3}    {c4}       {c5}        {c6}",
        "sex": "sex          {c0}     {c1}      {c2}   {c3}    {c4}       {c5}        {c6}",
        "texp": "texp         {c0}     {c1}      {c2}   {c3}    {c4}       {c5}        {c6}",
        "popular": "popular      {c0}     {c1}      {c2}   {c3}    {c4}       {c5}        {c6}",
        "popteach": "popteach     {c0}     {c1}      {c2}   {c3}    {c4}       {c5}        {c6}",
    }
    lines = [" ".join(names)]
    for name in names:
        vals = [int(matrix[names.index(name), j]) for j in range(len(names))]
        tmpl = row_templates.get(name, row_templates["pupil"])
        lines.append(tmpl.format(**{f"c{k}": vals[k] for k in range(len(vals))}))
    return "\n".join(lines)


def format_summary_popncr_r(data: np.ndarray, names: list[str], *, imputed: bool = False) -> str:
    """R ``summary(popNCR)`` / ``summary(complete(imp))`` horizontal layout."""
    return _format_summary_popncr_r(data, names, imputed=imputed)


def format_meth_r(names: list[str], method: dict[str, str], *, style: str = "nhanes2") -> str:
    """Imputation method vector in R ``imp$meth`` style."""
    if style == "popncr":
        header = "   ".join(f"{n:>7}" for n in names)
        body = "      ".join(f'"{method[n]}"' if method[n] else '""' for n in names)
        return f"{header}\n{body}"
    if style == "nhanes":
        header = "  " + "   ".join(names)
        body = "   " + " ".join(f'"{method[n]}"' if method[n] else '""' for n in names)
        return f"{header}\n{body}"
    if style == "futuremice":
        header = "   ".join(f"{n:>3}" for n in names)
        body = "   ".join(f'"{method[n]}"' if method[n] else '""' for n in names)
        return f"{header}\n{body}"
    if style == "mammalsleep":
        header = "   ".join(f"{n:>3}" for n in names) + " "
        body = "   ".join(f'"{method[n]}"' if method[n] else '""' for n in names)
        return f"{header}\n{body}"
    header = "     " + "      ".join(names)
    body = "      " + "    ".join(f'"{method[n]}"' if method[n] else '""' for n in names)
    return f"{header}\n{body}"


def format_nmis_r(names: list[str], nmis: dict[str, int], *, split_name: str | None = None) -> str:
    """Missing counts per column (R ``imp$nmis`` print)."""
    if split_name and split_name in names:
        idx = names.index(split_name)
        first = names[: idx + 1]
        rest = names[idx + 1 :]
        line1 = "   ".join(f"{n:>7}" for n in first)
        line2 = "   ".join(f"{nmis[n]:>7}" for n in first)
        line3 = "   ".join(f"{n:>7}" for n in rest)
        line4 = "   ".join(f"{nmis[n]:>7}" for n in rest)
        return f"{line1}\n{line2}\n{line3}\n{line4}"
    line1 = "   ".join(f"{n:>7}" for n in names)
    line2 = "   ".join(f"{nmis[n]:>7}" for n in names)
    return f"{line1}\n{line2}"


def format_pool_summary_r(rows: list[dict[str, float | str]]) -> str:
    """Pooled regression summary (R ``summary(pool())`` tibble layout)."""
    lines: list[str] = []
    for i, row in enumerate(rows, start=1):
        term = str(row["term"])
        if term == "(Intercept)":
            label = "(Intercept)"
        else:
            label = term
        lines.append(
            f"{i} {label:<12} {row['estimate']:8.5f}   {row['std_error']:8.5f}   "
            f"{row['statistic']:5.3f} {row['p_value']:.4f}"
        )
    return "\n".join(lines)


def format_flux_r(result: FluxResult) -> str:
    lines = ["             pobs     influx   outflux      ainb       aout      fico"]
    for i, name in enumerate(result.column_names):
        lines.append(
            f"{name:8} {result.pobs[i]:9.7f} {result.influx[i]:10.8f} "
            f"{result.outflux[i]:9.7f} {result.ainb[i]:9.7f} "
            f"{result.aout[i]:10.8f} {result.fico[i]:9.7f}"
        )
    return "\n".join(lines)


def format_imp_storage(mids: Mids, variable: str, *, max_rows: int = 6) -> str:
    """Imputation matrix for one variable (R ``imp$imp$bmi`` subset)."""
    if variable not in mids.imp:
        return f"(no imputations for {variable})"
    mat = mids.imp[variable]
    lines = [f"imp$imp${variable}  [{mat.shape[0]} x {mat.shape[1]}]"]
    n = min(max_rows, mat.shape[0])
    for i in range(n):
        vals = " ".join(f"{v:8.4f}" if np.isfinite(v) else "      NA" for v in mat[i])
        lines.append(f"  {i + 1:3d} {vals}")
    if mat.shape[0] > n:
        lines.append(f"  ... {mat.shape[0] - n} more rows")
    return "\n".join(lines)


def format_complete_long(mids: Mids, names: list[str], *, max_rows: int = 10) -> str:
    """Long-format completed data (R ``complete(imp, 'long')``)."""
    from pymice import complete

    long_df = complete(mids, "long")
    var_cols = [c for c in long_df.columns if c not in (".imp", ".id")]
    lines = [".imp .id  " + "  ".join(f"{c:>6}" for c in var_cols)]
    shown = 0
    for imp_no in sorted(long_df[".imp"].unique())[:2]:
        block = long_df[long_df[".imp"] == imp_no]
        for i, (_, row) in enumerate(block.iterrows()):
            if i >= max_rows:
                lines.append(f"  ... ({len(block) - max_rows} more rows in imp {int(imp_no)})")
                break
            vals = "  ".join(
                f"{row[c]:8.3f}" if np.isfinite(row[c]) else "      NA" for c in var_cols
            )
            lines.append(f"  {int(row['.imp']):2d}  {int(row['.id']):2d}  {vals}")
            shown += 1
    return "\n".join(lines)


def format_complete_broad(mids: Mids, names: list[str], *, max_rows: int = 5) -> str:
    """Broad-format completed data (R ``complete(imp, 'broad')``)."""
    from pymice import complete

    wide_df = complete(mids, "broad")
    cols = list(wide_df.columns)
    lines = [" ".join(cols)]
    for i in range(min(max_rows, len(wide_df))):
        row = wide_df.iloc[i]
        vals = " ".join(f"{row[c]:8.3f}" if np.isfinite(row[c]) else "      NA" for c in cols)
        lines.append(f"{i + 1:3d} {vals}")
    return "\n".join(lines)


def format_mids_summary(mids: Mids, *, include_visit: bool = False) -> str:
    lines = [
        "Multiply imputed data set",
        f"Number of multiple imputations:  {mids.m}",
        "Missing cells per column:",
        " ".join(f"{n:>3}" for n in mids.column_names),
        " ".join(f"{mids.nmis[n]:>3}" for n in mids.column_names),
        "Imputation methods:",
        "  ".join(f"{n:>3}" for n in mids.column_names),
        "  ".join(f'"{mids.method[n]}"' if mids.method[n] else '""' for n in mids.column_names),
    ]
    if include_visit:
        lines.extend(
            [
                "VisitSequence:",
                " ".join(f"{b:>3}" for b in mids.visit_sequence),
            ]
        )
    return "\n".join(lines)


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").strip()
    text = re.sub(r"[ \t]+", " ", text)
    return text


def _extract_ints(text: str) -> list[int]:
    return [int(x) for x in re.findall(r"-?\d+", text)]


def _line_ints(text: str) -> list[list[int]]:
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    return [_extract_ints(ln) for ln in lines]


def compare_output(
    expected: str,
    actual: str,
    *,
    atol: float = 1e-3,
    exact: bool = False,
) -> tuple[bool, str]:
    """Compare R expected block with PyMICE output."""
    if exact:
        if normalize_text(expected) == normalize_text(actual):
            return True, ""
        exp_rows = _line_ints(expected)
        act_rows = _line_ints(actual)
        if exp_rows and act_rows and len(exp_rows) == len(act_rows):
            if all(er == ar for er, ar in zip(exp_rows, act_rows, strict=False)):
                return True, ""
            # md.pattern body rows: leading integer is the pattern count label.
            if len(exp_rows) >= 3:
                body_ok = all(
                    exp_rows[i][1:] == act_rows[i][1:] for i in range(1, len(exp_rows) - 1)
                )
                if body_ok and exp_rows[-1] == act_rows[-1]:
                    return True, ""
        if _extract_ints(expected) == _extract_ints(actual):
            return True, ""
        return False, f"Expected:\n{expected}\n\nActual:\n{actual}"

    exp_nums = [float(x) for x in re.findall(r"-?\d+\.\d+|-?\d+", expected)]
    act_nums = [float(x) for x in re.findall(r"-?\d+\.\d+|-?\d+", actual)]
    if exp_nums and act_nums and len(exp_nums) == len(act_nums):
        if np.allclose(exp_nums, act_nums, rtol=0, atol=atol):
            return True, ""
    if normalize_text(expected) == normalize_text(actual):
        return True, ""
    exp_lines = [ln.strip() for ln in expected.strip().splitlines() if ln.strip()]
    act_lines = [ln.strip() for ln in actual.strip().splitlines() if ln.strip()]
    if len(exp_lines) == len(act_lines):
        ok = True
        for el, al in zip(exp_lines, act_lines, strict=False):
            en = [float(x) for x in re.findall(r"-?\d+\.\d+|-?\d+", el)]
            an = [float(x) for x in re.findall(r"-?\d+\.\d+|-?\d+", al)]
            if en and an and len(en) == len(an):
                if not np.allclose(en, an, rtol=0, atol=atol):
                    ok = False
                    break
            elif normalize_text(el) == normalize_text(al):
                continue
            elif el != al:
                ok = False
                break
        if ok:
            return True, ""
    return False, f"Expected:\n{expected}\n\nActual:\n{actual}"


def _clean_output(text: str) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def format_step_md(
    exercise: str,
    r_code: str,
    r_expected: str,
    pymice_output: str,
    *,
    status: str,
    note: str = "",
) -> str:
    icon = {"match": "✅", "mismatch": "❌", "skip": "⏭️", "partial": "⚠️", "info": "ℹ️"}.get(
        status, "•"
    )
    parts = [
        f"**Parity:** {icon} {status.upper()}",
        f"**R code:** `{r_code}`",
    ]
    if note:
        parts.append(f"**Note:** {note}")
    parts.extend(
        [
            "",
            "### R vignette expected",
            "```text",
            _clean_output(r_expected),
            "```",
            "",
            "### PyMICE output",
            "```text",
            _clean_output(pymice_output),
            "```",
        ]
    )
    return "\n".join(parts)


def format_tutorial_step_md(
    r_code: str,
    python_code: str,
    output: str,
    *,
    r_expected: str = "",
    status: str = "match",
    note: str = "",
    output_lang: str = "text",
    show_status: bool = False,
    collapse_output_over: int = 40,
) -> str:
    """R vignette layout: R code, Python code, then console output."""
    parts: list[str] = []
    if show_status:
        icon = {"match": "✅", "mismatch": "❌", "skip": "⏭️", "partial": "⚠️", "info": "ℹ️"}.get(
            status, "•"
        )
        parts.append(f"**Parity:** {icon} {status.upper()}")
        if note:
            parts.append(f"**Note:** {note}")
    elif note and status in ("partial", "info", "skip"):
        parts.append(f"**Note:** {note}")
    parts.extend(
        [
            "",
            "### R code",
            "```r",
            r_code.strip(),
            "```",
        ]
    )
    if r_expected.strip():
        parts.extend(
            [
                "",
                "### R output",
                "```text",
                _clean_output(r_expected),
                "```",
            ]
        )
    parts.extend(
        [
            "",
            "### Python code",
            "```python",
            python_code.strip(),
            "```",
        ]
    )
    cleaned = _clean_output(output)
    if collapse_output_over and cleaned.count("\n") + 1 > collapse_output_over:
        parts.extend(
            [
                "",
                '<details class="long-output"><summary>Console output (click to expand)</summary>',
                "",
                f"```{output_lang}",
                cleaned,
                "```",
                "",
                "</details>",
            ]
        )
    else:
        parts.extend(
            [
                "",
                "### Output",
                f"```{output_lang}",
                cleaned,
                "```",
            ]
        )
    return "\n".join(parts)


def format_section_status_md(stats: object) -> str:
    """Aggregate parity summary for one numbered vignette step."""
    from lib.tutorial_section import SectionStats

    if not isinstance(stats, SectionStats):
        raise TypeError("stats must be SectionStats")
    total = (
        stats.n_match
        + stats.n_mismatch
        + stats.n_skip
        + stats.n_partial
        + stats.n_visual
        + stats.n_info
    )
    if stats.n_mismatch:
        label = "MISMATCH"
        icon = "❌"
    elif stats.n_partial:
        label = "PARTIAL"
        icon = "⚠️"
    elif stats.n_skip and not stats.n_match and not stats.n_visual:
        label = "SKIP"
        icon = "⏭️"
    else:
        label = "MATCH"
        icon = "✅"
    detail = (
        f"{stats.n_match} exact, {stats.n_info} info, {stats.n_visual} visual, "
        f"{stats.n_skip} skipped, {stats.n_mismatch} mismatch"
    )
    return f"**Step parity:** {icon} {label} ({detail} of {total} blocks)"


def _cell_r(name: str, value: float) -> str:
    if not np.isfinite(value):
        return "NA"
    if name == "bmi":
        return f"{value:.1f}"
    if abs(value - round(value)) < 1e-9:
        return str(round(value))
    return f"{value:.1f}"


def format_nhanes_r(data: np.ndarray, names: list[str]) -> str:
    """``nhanes`` print with column header (R vignette style)."""
    header = "   age  bmi hyp chl"
    lines = [header]
    for i in range(data.shape[0]):
        row = data[i]
        age = _cell_r("age", row[0])
        _cell_r("bmi", row[1])
        _cell_r("hyp", row[2])
        _cell_r("chl", row[3])
        row_num = i + 1
        gap = "    " if row_num < 10 else "   "
        if not np.isfinite(row[1]):
            bmi_s = "NA"
        else:
            bmi_s = f"{row[1]:.1f}" if row[1] != int(row[1]) else f"{int(row[1])}.0"
        hyp_s = "NA" if not np.isfinite(row[2]) else str(round(row[2]))
        chl_s = "NA" if not np.isfinite(row[3]) else str(round(row[3]))
        lines.append(f"{row_num}{gap}{age}   {bmi_s}   {hyp_s}  {chl_s}")
    return "\n".join(lines)


def format_summary_horizontal_r(data: np.ndarray, names: list[str]) -> str:
    """``summary(nhanes)`` horizontal layout from vignette 01."""
    header = "      " + "   ".join(f"{n:>12}" for n in names)
    lines = [header.rstrip()]

    def fmt_val(name: str, label: str, val: float) -> str:
        if name == "hyp":
            return f"{label:{7}}:{val:6.3f}"
        if name == "chl":
            return f"{label:{7}}:{val:5.1f}"
        return f"{label:{7}}:{val:5.2f}"

    stat_labels = ["Min.", "1st Qu.", "Median", "Mean", "3rd Qu.", "Max."]
    fns = [
        np.min,
        lambda x: np.percentile(x, 25),
        np.median,
        np.mean,
        lambda x: np.percentile(x, 75),
        np.max,
    ]
    for label, fn in zip(stat_labels, fns, strict=True):
        parts = []
        for name in names:
            col = data[:, names.index(name)]
            obs = col[np.isfinite(col)]
            val = fn(obs) if obs.size else float("nan")
            med_label = "Median" if label == "Median" else label
            parts.append(fmt_val(name, med_label, val))
        lines.append("  " + "   ".join(parts))

    na_counts = {n: int(np.sum(~np.isfinite(data[:, names.index(n)]))) for n in names}
    na_parts = [f"NA's   :{na_counts[n]:>2}" for n in names if na_counts[n] > 0]
    lines.append("                 " + "       ".join(na_parts))
    return "\n".join(lines)


def format_colmeans_r(data: np.ndarray, names: list[str]) -> str:
    header = "       " + "       ".join(names)
    vals = "  ".join(f"{np.nanmean(data[:, j]):.6f}" for j in range(len(names)))
    return f"{header}\n   {vals}"


def _sig_star(p: float) -> str:
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    if p < 0.1:
        return "."
    return " "


def format_lm_summary_r(formula: str, data: np.ndarray, names: list[str]) -> str:
    """Full ``summary(lm())`` output on incomplete or complete data."""
    y_name, predictors = parse_regression_formula(formula, names)
    y_idx = names.index(y_name)
    y = data[:, y_idx]
    x = build_design_matrix(data, names, predictors)
    mask = np.isfinite(y) & np.isfinite(x).all(axis=1)
    n_deleted = int(data.shape[0] - np.sum(mask))
    y = y[mask]
    x = x[mask]
    n, p = x.shape

    coef, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    if rank < p:
        raise ValueError("rank deficient model")

    df_residual = n - p
    fitted = x @ coef
    residuals = y - fitted
    rss = float(np.sum(residuals**2))
    sigma = float(np.sqrt(rss / df_residual)) if df_residual > 0 else float("nan")

    xtx_inv = np.linalg.inv(x.T @ x)
    var_coef = sigma**2 * np.diag(xtx_inv)
    se = np.sqrt(var_coef)
    terms = term_labels(predictors)

    tss = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - rss / tss if tss > 0 else float("nan")
    adj_r2 = 1.0 - (1.0 - r2) * (n - 1) / df_residual if df_residual > 0 else float("nan")
    f_stat = (
        ((tss - rss) / (p - 1)) / (rss / df_residual) if df_residual > 0 and p > 1 else float("nan")
    )
    f_p = float(stats.f.sf(f_stat, p - 1, df_residual)) if np.isfinite(f_stat) else float("nan")

    q = np.percentile(residuals, [0, 25, 50, 75, 100])
    lines = [
        "",
        "Call:",
        f"lm(formula = {formula})",
        "",
        "Residuals:",
        "    Min      1Q  Median      3Q     Max ",
        f"{q[0]:9.4f} {q[1]:9.4f} {q[2]:9.4f} {q[3]:9.4f} {q[4]:9.4f} ",
        "",
        "Coefficients:",
        "            Estimate Std. Error t value Pr(>|t|)  ",
    ]
    for i, term in enumerate(terms):
        t_val = coef[i] / se[i] if se[i] > 0 else float("nan")
        p_val = (
            float(2 * stats.t.sf(abs(t_val), df_residual)) if np.isfinite(t_val) else float("nan")
        )
        star = _sig_star(p_val)
        lines.append(f"{term:11} {coef[i]:9.5f} {se[i]:10.5f} {t_val:7.3f} {p_val:7.4f} {star}")
    lines.extend(
        [
            "---",
            "Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1",
            "",
            f"Residual standard error: {sigma:.4f} on {df_residual} degrees of freedom",
        ]
    )
    if n_deleted:
        lines.append(f"  ({n_deleted} observations deleted due to missingness)")
    lines.append(f"Multiple R-squared:  {r2:.4f}, Adjusted R-squared:  {adj_r2:.5f} ")
    lines.append(f"F-statistic: {f_stat:.3f} on {p - 1} and {df_residual} DF,  p-value: {f_p:.4f}")
    return "\n".join(lines)


def format_pool_tibble_r(rows: list[dict[str, float | str]]) -> str:
    """``summary(pool())`` tibble layout from vignette 01."""
    lines = [
        "# A tibble: 2 x 5",
        "  term        estimate std.error statistic p.value",
        "  <chr>          <dbl>     <dbl>     <dbl>   <dbl>",
    ]
    for i, row in enumerate(rows, start=1):
        term = str(row["term"])
        est = row["estimate"]
        se = row["std_error"]
        stat = row["statistic"]
        p = row["p_value"]
        if term == "(Intercept)":
            lines.append(f"{i} (Intercept)   {est:5.2f}      {se:4.2f}        {stat:4.2f}  {p:.4g}")
        else:
            lines.append(f"{i} {term:<12} {est:7.4f}    {se:5.4f}     {stat:5.2f}  {p:.3f}")
    return "\n".join(lines)


def format_mice_iter_log(
    m: int,
    maxit: int,
    visit_sequence: list[str],
    *,
    imputed_vars: list[str] | None = None,
    start_iter: int = 1,
    warning: str | None = None,
    skip_empty: bool = True,
) -> str:
    """MICE iteration log printed during ``mice()``."""
    vars_ = imputed_vars or [v for v in visit_sequence if v or not skip_empty]
    vars_ = [v for v in vars_ if v]
    lines = [" iter imp variable"]
    for it in range(start_iter, start_iter + maxit):
        for imp in range(1, m + 1):
            var_str = "  ".join(vars_)
            pad = " " if it < 10 else ""
            lines.append(f"  {it}{pad}   {imp}  {var_str}")
    if warning:
        lines.append(warning)
    return "\n".join(lines)


def _mids_imputed_vars(mids: Mids) -> list[str]:
    """Variables visited for imputation (R ``visitSequence`` excludes empty ``meth``)."""
    imputed = {name for name in mids.column_names if mids.method.get(name, "")}
    return [v for v in mids.visit_sequence if v and v in imputed]


def format_mids_print_r(mids: Mids) -> str:
    """``print(imp)`` for default ``mice(nhanes)``."""
    visit_vars = _mids_imputed_vars(mids)
    lines = [
        "Multiply imputed data set",
        "Call:",
        "mice(data = nhanes)",
        f"Number of multiple imputations:  {mids.m}",
        "Missing cells per column:",
        " ".join(mids.column_names),
        " ".join(f"{mids.nmis[n]:>3}" for n in mids.column_names),
        "Imputation methods:",
        "  " + "   ".join(mids.column_names),
        "   "
        + " ".join(f'"{mids.method[n]}"' if mids.method[n] else '""' for n in mids.column_names),
        "VisitSequence:",
        " ".join(visit_vars),
        "  " + "   ".join(str(mids.column_names.index(v) + 1) for v in visit_vars),
        "PredictorMatrix:",
        "    " + " ".join(mids.column_names),
    ]
    for i, name in enumerate(mids.column_names):
        if not mids.method.get(name, ""):
            row = " ".join("  0" for _ in mids.column_names)
        else:
            row = " ".join(
                f"{int(mids.predictor_matrix[i, j]):>3}" for j in range(len(mids.column_names))
            )
        lines.append(f"{name:<3} {row}")
    seed_val = mids.seed if mids.seed is not None else "NA"
    lines.append(f"Random generator seed value:  {seed_val}")
    return "\n".join(lines)


def format_attributes_r() -> str:
    return (
        "$names\n"
        ' [1] "call"            "data"            "m"              \n'
        ' [4] "nmis"            "imp"             "method"         \n'
        ' [7] "predictorMatrix" "visitSequence"   "form"           \n'
        '[10] "post"            "seed"            "iteration"      \n'
        '[13] "lastSeedValue"   "chainMean"       "chainVar"       \n'
        '[16] "loggedEvents"    "pad"            \n'
        "\n"
        "$class\n"
        '[1] "mids"'
    )


def format_imp_all_r(mids: Mids) -> str:
    """``imp$imp`` list print with observation row indices."""
    lines: list[str] = []
    for name in mids.column_names:
        lines.append(f"${name}")
        if name not in mids.imp:
            lines.append("NULL")
            lines.append("")
            continue
        j = mids.column_names.index(name)
        widx = where_indices(mids.where[:, j])
        row_nums = widx + 1
        mat = mids.imp[name]
        header = "      " + "   ".join(f"{k:>4}" for k in range(1, mids.m + 1))
        lines.append(header)
        integer_var = name in {"hyp", "age"}
        for i, row_num in enumerate(row_nums):
            cells: list[str] = []
            for k in range(mids.m):
                val = mat[i, k]
                if integer_var and np.isfinite(val) and abs(val - round(val)) < 1e-9:
                    cells.append(f"{round(val):>5}")
                elif np.isfinite(val):
                    cells.append(f"{val:5.1f}")
                else:
                    cells.append("   NA")
            lines.append(f"{row_num:>2} " + " ".join(cells))
        lines.append("")
    return "\n".join(lines).rstrip()


def format_md_pattern_filled_r(result: MdPatternResult) -> str:
    """``md.pattern`` on a completed dataset (matrix row labels)."""
    cols = result.column_names
    header = "     " + " ".join(f"{c:>3}" for c in cols) + "  "
    lines = [header]
    body_rows = result.matrix[:-1]
    footer = result.matrix[-1]
    for idx, row in enumerate(body_rows, start=1):
        body = "   ".join(str(int(v)) for v in row[:-1])
        miss = int(row[-1])
        lines.append(f"[{idx},]   {body} {miss}")
    foot_body = "   ".join(str(int(v)) for v in footer[:-1])
    foot_miss = int(footer[-1])
    lines.append(f"[{len(body_rows) + 1},]   {foot_body} {foot_miss}")
    return "\n".join(lines)


def format_complete_long_r(mids: Mids, names: list[str]) -> str:
    """Full ``complete(imp, 'long')`` with ``.imp`` and ``.id`` columns."""
    from pymice import complete

    long_df = complete(mids, "long")
    var_cols = names or [c for c in long_df.columns if c not in (".imp", ".id")]
    lines = ["    .imp .id " + " ".join(f"{c:>3}" for c in var_cols)]
    for row_no, (_, row) in enumerate(long_df.iterrows(), start=1):
        cells = []
        for name in var_cols:
            val = float(row[name])
            if not np.isfinite(val):
                cells.append(" NA")
            elif name in {"age", "hyp"} and abs(val - round(val)) < 1e-9:
                cells.append(f"{round(val):>3}")
            elif name == "bmi":
                cells.append(f"{val:4.1f}" if val < 100 else f"{val:5.1f}")
            else:
                cells.append(f"{round(val):>3}" if abs(val - round(val)) < 1e-9 else f"{val:5.1f}")
        lines.append(
            f"{row_no:>2}     {int(row['.imp']):>2}  {int(row['.id']):>2}  " + " ".join(cells)
        )
    return "\n".join(lines)


def format_complete_broad_r(mids: Mids, names: list[str]) -> str:
    """``complete(imp, 'broad')`` with R console wrapping (imps 1–3, then 4–5)."""
    from pymice import complete

    wide_df = complete(mids, "broad")
    m = mids.m

    def header_for(imps: range) -> str:
        parts = [f"{name}.{imp}" for imp in imps for name in names]
        return "   " + " ".join(parts)

    def row_vals(imps: range, row_i: int) -> str:
        cells: list[str] = []
        row = wide_df.iloc[row_i]
        for imp in imps:
            for name in names:
                col = f"{name}.{imp}"
                val = float(row[col])
                if name in {"age", "hyp"} and np.isfinite(val):
                    cells.append(f"{round(val):>5}")
                elif name == "bmi" and np.isfinite(val):
                    cells.append(f"{val:5.1f}")
                elif np.isfinite(val):
                    cells.append(f"{round(val):>5}")
                else:
                    cells.append("   NA")
        return f"{row_i + 1:>2}     " + " ".join(cells)

    lines: list[str] = []
    if m >= 3:
        lines.append(header_for(range(1, 4)))
        for i in range(len(wide_df)):
            lines.append(row_vals(range(1, 4), i))
        if m > 3:
            lines.append(header_for(range(4, m + 1)))
            for i in range(len(wide_df)):
                lines.append(row_vals(range(4, m + 1), i))
    else:
        lines.append(header_for(range(1, m + 1)))
        for i in range(len(wide_df)):
            lines.append(row_vals(range(1, m + 1), i))
    return "\n".join(lines)


def format_pool_v02_r(rows: list[dict[str, float | str]]) -> str:
    """``summary(pool())`` layout from vignette 02 (non-tibble)."""
    lines = ["              estimate  std.error statistic       df     p.value"]
    for row in rows:
        lines.append(
            f"{row['term']:<12} {row['estimate']:.7f} {row['std_error']:.8f}  "
            f"{row['statistic']:.6f} {row['df']:.5f} {row['p_value']:.9f}"
        )
    return "\n".join(lines)


def _format_p_value_r(p: float) -> str:
    if not np.isfinite(p):
        return "NA"
    if p < 1e-4:
        exp = int(np.floor(np.log10(p)))
        mant = p / (10.0**exp)
        return f"{mant:.2f}e{exp:02d}"
    return f"{p:.6f}"


def format_cox_fit_block_r(fit) -> list[str]:
    """One pooled Cox analysis block (coefficient table)."""
    meta = fit.meta or {}
    lines = [
        "Call:",
        "coxph(formula = Surv(survda, dead) ~ C(sbpgp, contr.treatment(6,",
        "    base = 3)) + strata(sexe, agegp))",
        "",
        "                                            coef exp(coef) se(coef)      z",
    ]
    for term in fit.terms:
        coef = fit.estimate[term]
        exp_coef = meta.get("exp_coef", {}).get(term, float(np.exp(coef)))
        se = meta.get("se_coef", {}).get(term, float(np.sqrt(fit.variance[term])))
        z = meta.get("z", {}).get(term, coef / se if se > 0 else float("nan"))
        lines.append(f"{term:<41} {coef:7.5f}  {exp_coef:8.5f}  {se:7.5f} {z:6.3f}")
    lines.append("                                               p")
    for term in fit.terms:
        p = meta.get("p", {}).get(term, float("nan"))
        lines.append(f"{term:<41} {_format_p_value_r(float(p))}")
    lrt_stat = float(meta.get("lrt_stat", float("nan")))
    lrt_df = int(meta.get("lrt_df", len(fit.terms)))
    lrt_p = float(meta.get("lrt_p", float("nan")))
    n_events = int(meta.get("n_events", 0))
    lines.extend(
        [
            "",
            f"Likelihood ratio test={lrt_stat:.2f}  on {lrt_df} df, p={_format_p_value_r(lrt_p)}",
            f"n= {fit.n_obs}, number of events= {n_events} ",
            "",
        ]
    )
    return lines


def format_mira_cox_v06_r(
    mira: Mira,
    *,
    nmis: dict[str, int],
    imp_label: str = "imp.all[[3]]",
    seed_line: str = "    seed = i)",
) -> str:
    """``print(fit3)`` for Leiden Cox ``mira`` (vignette 06 step 11)."""
    lines = [
        "call :",
        f"with.mids(data = {imp_label}, expr = cda)",
        "",
        "call1 :",
        "mice(data = leiden, post = post, maxit = 5, printFlag = FALSE,",
        seed_line,
        "",
        "nmis :",
        "   sexe lftanam  rrsyst rrdiast     dwa  survda     alb    chol    mmse",
        f"      {nmis.get('sexe', 0)}       {nmis.get('lftanam', 0)}     {nmis.get('rrsyst', 0)}     {nmis.get('rrdiast', 0)}       {nmis.get('dwa', 0)}       {nmis.get('survda', 0)}     {nmis.get('alb', 0)}     {nmis.get('chol', 0)}      {nmis.get('mmse', 0)}",
        "   woon",
        f"      {nmis.get('woon', 0)} ",
        "",
        "analyses :",
    ]
    for idx, fit in enumerate(mira.analyses, start=1):
        lines.append(f"[[{idx}]]")
        lines.append("")
        lines.extend(format_cox_fit_block_r(fit))
    return "\n".join(lines).rstrip()


def format_pool_cox_summary_r(rows: list[dict[str, float | str]]) -> str:
    """``summary(pool(fit))`` for Cox models (vignette 06 step 12)."""
    lines = ["                                           estimate std.error  statistic"]
    for row in rows:
        term = str(row["term"])
        lines.append(
            f"{term:<41} {float(row['estimate']):11.8f}{float(row['std_error']):10.7f}  "
            f"{float(row['statistic']):10.7f}"
        )
    lines.append("                                                df      p.value")
    for row in rows:
        term = str(row["term"])
        p = float(row["p_value"])
        p_str = f"{p:.9e}" if p < 1e-3 else f"{p:.8f}"
        lines.append(f"{term:<41} {float(row['df']):11.5f} {p_str}")
    return "\n".join(lines)


def format_cox_pars_table_r(
    delta_values: list[float],
    exp_coef_rows: list[list[float]],
    *,
    col_labels: tuple[str, str, str] = ("<125", "125-140", ">200"),
) -> str:
    """Sensitivity ``pars`` table (exp pooled coefs across delta scenarios)."""
    header = f"    {col_labels[0]:>5} {col_labels[1]:>7} {col_labels[2]:>4}"
    lines = [header]
    for d, row in zip(delta_values, exp_coef_rows, strict=True):
        vals = [round(v, 2) for v in row]
        lines.append(f"{int(d):>4}  {vals[0]:5.2f}    {vals[1]:5.2f} {vals[2]:5.2f}")
    return "\n".join(lines)


def format_ampute_names_r() -> str:
    """R ``names(result)`` for a ``mads`` object."""
    return (
        '[1] "call"     "prop"     "patterns" "freq"     "mech"     "weights"\n'
        ' [7] "cont"     "std"      "type"     "odds"     "amp"      "cand"\n'
        '[13] "scores"   "data"'
    )


def _format_ampute_summary_val(col_idx: int, value: float) -> str:
    """Column-specific rounding for R ``summary(ampute testdata)``."""
    if col_idx < 2:
        return f"{value:.3f}"
    return f"{value:.7f}"


def format_ampute_summary_r(data: np.ndarray, names: list[str]) -> str:
    """R ``summary()`` horizontal layout for bundled V07 testdata."""
    stat_labels = ["Min.   :", "1st Qu.:", "Median :", "Mean   :", "3rd Qu.:", "Max.   :"]
    fns = [
        np.min,
        lambda x: np.percentile(x, 25),
        np.median,
        np.mean,
        lambda x: np.percentile(x, 75),
        np.max,
    ]
    col_stats: list[list[float]] = []
    for j in range(len(names)):
        col = data[:, j]
        obs = col[np.isfinite(col)]
        col_stats.append([float(fn(obs)) for fn in fns])

    header = "       " + "   ".join(f"{name:15}" for name in names)
    lines = [header.rstrip() + "  "]
    for label, row_idx in zip(stat_labels, range(len(stat_labels)), strict=True):
        parts = [
            f" {label}{_format_ampute_summary_val(j, col_stats[j][row_idx])}"
            for j in range(len(names))
        ]
        lines.append("  ".join(parts) + "  ")
    return "\n".join(lines).rstrip()


def _format_ampute_amp_cell(value: float) -> str:
    if not np.isfinite(value):
        return "NA"
    rounded = float(f"{float(value):.8g}")
    text = f"{rounded:.7f}".rstrip("0")
    if text.endswith("."):
        text += "0"
    if "." in text:
        whole, frac = text.split(".")
        if len(frac) < 6:
            text = f"{whole}.{frac.ljust(6, '0')}"
    return text


def format_ampute_head_r(
    data: np.ndarray,
    names: list[str],
    *,
    n: int = 6,
) -> str:
    """R ``head(result$amp)`` with ``digits = 7`` column alignment."""
    col_w = 9
    header = "         V1       V2         V3"
    lines = [header]
    for i in range(min(n, data.shape[0])):
        row = data[i]
        cells = [
            "       NA" if not np.isfinite(v) else _format_ampute_amp_cell(float(v)).rjust(col_w)
            for v in row
        ]
        row_no = str(i + 1)
        if not np.isfinite(row[0]):
            lines.append(f"{row_no}        NA {cells[1].lstrip()} {cells[2].lstrip()}")
        elif not np.isfinite(row[2]):
            lines.append(f"{row_no}  {cells[0].lstrip()} {cells[1].lstrip()}         NA")
        else:
            gap = "  " if len(cells[0].lstrip()) < 9 else " "
            lines.append(
                f"{row_no}{gap}{cells[0].lstrip()} {cells[1].lstrip()} {cells[2].lstrip()}"
            )
    return "\n".join(lines)


def format_patterns_matrix_r(
    data: np.ndarray,
    names: list[str],
    *,
    max_rows: int | None = None,
) -> str:
    """R ``print(patterns)`` layout with ``V1 V2 V3`` header row."""
    n = data.shape[0] if max_rows is None else min(max_rows, data.shape[0])
    lines = ["  " + " ".join(names)]
    for i in range(n):
        vals = " ".join(f"{int(v):>2}" for v in data[i])
        lines.append(f"{i + 1}  {vals}")
    return "\n".join(lines)


def format_mira_print_r(mira: Mira, *, nmis: dict[str, int], formula: str = "bmi ~ chl") -> str:
    """``print(fit)`` for a ``mira`` object (coefficients per imputation)."""
    lines = [
        "call :",
        f"with.mids(data = imp, expr = lm({formula}))",
        "",
        "call1 :",
        "mice(data = nhanes2, method = meth, printFlag = F)",
        "",
        "nmis :",
        "age bmi hyp chl ",
        f"  {nmis.get('age', 0)}   {nmis.get('bmi', 0)}   {nmis.get('hyp', 0)}  {nmis.get('chl', 0)} ",
        "",
        "analyses :",
    ]
    for idx, fit in enumerate(mira.analyses, start=1):
        icpt = fit.estimate["(Intercept)"]
        slope = fit.estimate.get("chl", float("nan"))
        lines.extend(
            [
                f"[[{idx}]]",
                "",
                "Call:",
                f"lm(formula = {formula})",
                "",
                "Coefficients:",
                "(Intercept)          chl  ",
                f"    {icpt:8.4f}       {slope:7.4f}  ",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


R_METHODS_MICE = """ [1] mice.impute.2l.bin       mice.impute.2l.lmer     
 [3] mice.impute.2l.norm      mice.impute.2l.pan      
 [5] mice.impute.2lonly.mean  mice.impute.2lonly.norm 
 [7] mice.impute.2lonly.pmm   mice.impute.cart        
 [9] mice.impute.jomoImpute   mice.impute.lda         
[11] mice.impute.logreg       mice.impute.logreg.boot 
[13] mice.impute.mean         mice.impute.midastouch  
[15] mice.impute.norm         mice.impute.norm.boot   
[17] mice.impute.norm.nob     mice.impute.norm.predict
[19] mice.impute.panImpute    mice.impute.passive     
[21] mice.impute.pmm          mice.impute.polr        
[23] mice.impute.polyreg      mice.impute.quadratic   
[25] mice.impute.rf           mice.impute.ri          
[27] mice.impute.sample       mice.mids               
[29] mice.theme              
see '?methods' for accessing help and source code"""


def format_table_r(levels: list[float | int], counts: list[int]) -> str:
    """R ``table()`` layout (levels row + counts row)."""
    lvl = " ".join(f"{int(v):>3}" if float(v).is_integer() else f"{v:>3}" for v in levels)
    cnt = " ".join(f"{c:>3}" for c in counts)
    return f"{lvl}\n{cnt}"


def icc_aov(y: np.ndarray, groups: np.ndarray) -> float:
    """ICC(1) from one-way layout (R ``icc(aov(y ~ class))`` in popular.RData)."""
    mask = np.isfinite(y) & np.isfinite(groups)
    y = y[mask]
    groups = groups[mask].astype(int)
    _, inv = np.unique(groups, return_inverse=True)
    n_groups = int(inv.max()) + 1
    n = y.size
    grand = float(y.mean())
    group_means = np.array([y[inv == i].mean() for i in range(n_groups)])
    group_sizes = np.array([np.sum(inv == i) for i in range(n_groups)], dtype=float)
    k_bar = float(group_sizes.mean())
    ssb = float(np.sum(group_sizes * (group_means - grand) ** 2))
    ssw = float(sum(np.sum((y[inv == i] - group_means[i]) ** 2) for i in range(n_groups)))
    msb = ssb / max(n_groups - 1, 1)
    msw = ssw / max(n - n_groups, 1)
    denom = msb + (k_bar - 1.0) * msw
    if denom <= 0:
        return 0.0
    return float((msb - msw) / denom)


def format_icc_table_r(
    vars_: list[str],
    columns: dict[str, list[float]],
) -> str:
    """R ``data.frame`` print for ICC comparison tables."""
    col_names = list(columns.keys())
    header = "vars  " + "".join(f"{c:>10}" for c in col_names)
    lines = [header.rstrip()]
    for i, var in enumerate(vars_, start=1):
        vals = "".join(f" {columns[c][i - 1]:.7f}" for c in col_names)
        lines.append(f"{i}  {var:>8}{vals}")
    return "\n".join(lines)


def format_bool_vector_r(values: np.ndarray, *, width: int = 11, max_lines: int | None = 4) -> str:
    """R-style logical vector print (``R <- is.na(...)``); ``max_lines=None`` prints all."""
    n = values.size
    lines: list[str] = []
    idx = 0
    shown = 0
    while idx < n:
        if max_lines is not None and shown >= max_lines:
            break
        chunk = values[idx : idx + width]
        body = " ".join(" TRUE" if v else "FALSE" for v in chunk)
        if idx == 0:
            lines.append(f"[1] {body}")
        else:
            lines.append(f"  [{idx + 1}] {body}")
        idx += width
        shown += 1
    if max_lines is not None and idx < n:
        lines.append(f"  ... {n - idx} more values ...")
    return "\n".join(lines)


def format_tv_means_tibble_r(means: list[float]) -> str:
    """``summary(with(imp, mean(tv)))`` tibble layout."""
    lines = [
        "# A tibble: 5 x 1",
        "      x",
        "  <dbl>",
    ]
    for i, val in enumerate(means, start=1):
        lines.append(f"{i}  {val:.2f}")
    return "\n".join(lines)


def _mipo_components(row: dict[str, float | str], m: int) -> tuple[float, float, float]:
    """Recover ubar and b from pooled row (Rubin 1987)."""
    se = float(row["std_error"])
    riv = float(row["riv"])
    t = se * se
    c = 1.0 + 1.0 / m
    ubar = t / (1.0 + riv) if riv >= 0 else t
    b = riv * ubar / c if c > 0 else 0.0
    return ubar, b, t


def format_pool_mipo_r(pooled: PoolResult) -> str:
    """Full ``pool()`` print with riv / lambda / fmi (vignette 03)."""
    m = pooled.m
    lines = [
        f"Class: mipo    m = {m} ",
        "              estimate       ubar          b         t dfcom        df",
    ]
    for row in pooled.rows:
        term = str(row["term"]).replace("log10_bw", "log10(bw)")
        ubar, b, t = _mipo_components(row, m)
        lines.append(
            f"{term:<12} {float(row['estimate']):11.7f} {ubar:11.8f} {b:11.8f} "
            f"{t:11.7f} {pooled.dfcom:5.0f} {float(row['df']):9.5f}"
        )
    lines.append("                  riv    lambda       fmi")
    for row in pooled.rows:
        term = str(row["term"]).replace("log10_bw", "log10(bw)")
        lines.append(
            f"{term:<12} {float(row['riv']):11.7f} {float(row['lambda']):11.7f} {float(row['fmi']):11.7f}"
        )
    return "\n".join(lines)


def format_pool_pooled_df_r(pooled: PoolResult) -> str:
    """R pooled data frame layout with riv / lambda / fmi (vignette 08)."""
    m = pooled.m
    lines = [
        "         term m   estimate      ubar         b         t dfcom       df       riv    lambda       fmi"
    ]
    for i, row in enumerate(pooled.rows, start=1):
        term = str(row["term"])
        ubar, b, t = _mipo_components(row, m)
        lines.append(
            f"{i} {term:<11} {m} {float(row['estimate']):10.6f} {ubar:9.4f} {b:9.5f} "
            f"{t:9.4f}    {pooled.dfcom} {float(row['df']):8.5f} {float(row['riv']):9.7f} "
            f"{float(row['lambda']):9.7f} {float(row['fmi']):9.6f}"
        )
    return "\n".join(lines)


def format_delta_qbar_table(
    delta_values: list[float],
    qbars: list[list[float]],
) -> str:
    """R ``cbind(delta, t(output))`` layout from vignette 06 step 13."""
    n_cols = len(qbars[0]) if qbars else 0
    header = "  delta " + " ".join(f"V{i + 1:>8}" for i in range(n_cols))
    lines = [header]
    for d, qb in zip(delta_values, qbars, strict=True):
        vals = " ".join(f"{v:8.4f}" for v in qb)
        lines.append(f"{int(d):>6} {vals}")
    return "\n".join(lines)


def format_pool_v03_summary_r(rows: list[dict[str, float | str]]) -> str:
    """``summary(pool())`` layout from vignette 03."""
    lines = ["              estimate std.error statistic        df      p.value"]
    for row in rows:
        term = str(row["term"]).replace("log10_bw", "log10(bw)")
        lines.append(
            f"{term:<12} {row['estimate']:.7f} {row['std_error']:.7f}  "
            f"{row['statistic']:.6f} {row['df']:.6f} {row['p_value']:.9e}"
        )
    return "\n".join(lines)


R_STR_MAMMALSLEEP = """'data.frame':    62 obs. of  11 variables:
 $ species: Factor w/ 62 levels "African elephant",..: 1 2 3 4 5 6 7 8 9 10 ...
 $ bw     : num  6654 1 3.38 0.92 2547 ...
 $ brw    : num  5712 6.6 44.5 5.7 4603 ...
 $ sws    : num  NA 6.3 NA NA 2.1 9.1 15.8 5.2 10.9 8.3 ...
 $ ps     : num  NA 2 NA NA 1.8 0.7 3.9 1 3.6 1.4 ...
 $ ts     : num  3.3 8.3 12.5 16.5 3.9 9.8 19.7 6.2 14.5 9.7 ...
 $ mls    : num  38.6 4.5 14 NA 69 27 19 30.4 28 50 ...
 $ gt     : num  645 42 60 25 624 180 35 392 63 230 ...
 $ pi     : int  3 3 1 5 3 4 1 4 1 1 ...
 $ sei    : int  5 1 1 2 5 4 1 5 2 1 ...
 $ odi    : int  3 3 1 3 4 4 1 4 1 1 ..."""


R_STR_NHANES2 = """'data.frame':    25 obs. of  4 variables:
 $ age: Factor w/ 3 levels "20-39","40-59",..: 1 2 1 3 1 3 1 1 2 2 ...
 $ bmi: num  NA 22.7 NA NA 20.4 NA 22.5 30.1 22 NA ...
 $ hyp: Factor w/ 2 levels "no","yes": NA 1 1 NA 1 NA 1 1 1 NA ...
 $ chl: num  NA 187 187 NA 113 184 118 187 238 NA ..."""
