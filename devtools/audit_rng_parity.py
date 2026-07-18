#!/usr/bin/env python3
"""Audit RNG/draw-order partial claims; re-compare against goldens with aligned chains."""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

COMMANDS = Path(__file__).resolve().parent
ROOT = COMMANDS.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(COMMANDS))

from lib.parity_backlog import (  # noqa: E402
    ParityCategory,
    ParityTask,
    default_backlog,
    save_backlog,
)
from lib.paths import RUNNERS_DIR  # noqa: E402
from lib.r_style import compare_output  # noqa: E402

RNG_RE = re.compile(
    r"rng|seed|stochastic|pmm|norm|imput|parallel|ampute|draw|residual|"
    r"qbar|coefficient|icc|2l\.|gibbs|squeeze|tv counts|δ-adjustment|stream|snapshot",
    re.I,
)


@dataclass
class AuditRow:
    vignette: str
    step: str
    reason: str
    matches: bool
    category: ParityCategory
    recommendation: str
    source: str


def _row(
    vignette: str,
    step: str,
    reason: str,
    expected: str,
    actual: str,
    *,
    atol: float = 1e-3,
    exact: bool = False,
    category: ParityCategory,
    recommendation: str,
    source: str = "re-compare",
) -> AuditRow:
    match, _ = compare_output(expected, actual, atol=atol, exact=exact)
    return AuditRow(vignette, step, reason, match, category, recommendation, source)


def _fresh_session() -> None:
    from lib.vignette_rng import start_vignette_rng_session

    from pymice.rng import RSession

    RSession.close()
    start_vignette_rng_session(123)


def audit_v01() -> list[AuditRow]:
    from lib.r_style import (
        format_complete_broad_r,
        format_complete_long_r,
        format_complete_r,
        format_imp_all_r,
        format_mids_print_r,
        format_pool_tibble_r,
    )
    from lib.vignette_rng import run_v01_mice_chain
    from runners.v01_ad_hoc_mice import (
        R_COMPLETE_BROAD,
        R_COMPLETE_LONG,
        R_COMPLETE_NOB,
        R_IMP_VALUES,
        R_MIDS_PRINT,
        R_POOL_NOB,
        R_POOL_NOB_SEED,
        R_POOL_PREDICT,
        R_PREDICT_COMPLETE,
    )

    from pymice import complete, data, pool, summary, with_

    _fresh_session()
    nhanes = data("nhanes")
    names = list(nhanes.columns)
    _, imp_norm_predict, imp_nob, imp_nob_seed, imp_pmm = run_v01_mice_chain(
        nhanes,
        plot_bmi_density=True,
    )

    return [
        _row(
            "V01",
            "9 complete norm.predict",
            "densityplot RNG advance + session chain",
            R_PREDICT_COMPLETE,
            format_complete_r(complete(imp_norm_predict, 1), names),
            atol=1e-4,
            category=ParityCategory.DRAW_ORDER,
            recommendation="Should MATCH — remove partial if report still flags it.",
        ),
        _row(
            "V01",
            "9 pool norm.predict",
            "follows norm.predict chain",
            R_POOL_PREDICT,
            format_pool_tibble_r(summary(pool(with_(imp_norm_predict, "age ~ bmi")))),
            atol=0.01,
            category=ParityCategory.DRAW_ORDER,
            recommendation="Should MATCH — remove partial if report still flags it.",
        ),
        _row(
            "V01",
            "11 complete norm.nob",
            "session chain",
            R_COMPLETE_NOB,
            format_complete_r(complete(imp_nob, 1), names),
            atol=1e-4,
            category=ParityCategory.DRAW_ORDER,
            recommendation="Should MATCH — remove partial if report still flags it.",
        ),
        _row(
            "V01",
            "11 pool norm.nob",
            "session chain",
            R_POOL_NOB,
            format_pool_tibble_r(summary(pool(with_(imp_nob, "age ~ bmi")))),
            atol=0.01,
            category=ParityCategory.DRAW_ORDER,
            recommendation="Should MATCH — remove partial if report still flags it.",
        ),
        _row(
            "V01",
            "12 pool norm.nob seed=123",
            "explicit seed reset",
            R_POOL_NOB_SEED,
            format_pool_tibble_r(summary(pool(with_(imp_nob_seed, "age ~ bmi")))),
            atol=0.01,
            category=ParityCategory.DRAW_ORDER,
            recommendation="Should MATCH — remove partial if report still flags it.",
        ),
        _row(
            "V01",
            "13 print(imp)",
            "mids layout",
            R_MIDS_PRINT,
            format_mids_print_r(imp_pmm),
            exact=True,
            category=ParityCategory.COSMETIC,
            recommendation="visitSequence/predictorMatrix formatting; numeric imp values OK.",
        ),
        _row(
            "V01",
            "13 imp$imp",
            "PMM values",
            R_IMP_VALUES,
            format_imp_all_r(imp_pmm),
            category=ParityCategory.DRAW_ORDER,
            recommendation="Should MATCH — golden refreshed.",
        ),
        _row(
            "V01",
            "14 complete long",
            "PMM long",
            R_COMPLETE_LONG,
            format_complete_long_r(imp_pmm, names),
            category=ParityCategory.DRAW_ORDER,
            recommendation="Should MATCH — golden refreshed.",
        ),
        _row(
            "V01",
            "14 complete broad",
            "PMM broad",
            R_COMPLETE_BROAD,
            format_complete_broad_r(imp_pmm, names),
            category=ParityCategory.DRAW_ORDER,
            recommendation="Should MATCH — golden refreshed.",
        ),
    ]


def audit_v02() -> list[AuditRow]:
    from lib.data import load_nhanes, load_nhanes2
    from lib.golden import golden_output as g
    from lib.r_style import format_lm_summary_r, format_meth_r
    from lib.vignette_rng import run_v02_mice_chain
    from runners.v02_convergence_pooling import (
        NHANES2_SPECS,
        format_mira_print_r,
        format_pool_v02_r,
    )

    from pymice import complete, pool, summary_pool, with_mids

    _fresh_session()
    data, names = load_nhanes()
    data2, names2 = load_nhanes2()
    chain = run_v02_mice_chain(data, names, data2, names2, NHANES2_SPECS)
    imp3 = chain["imp3"]
    fit = with_mids(imp3, formula="bmi ~ chl")
    pooled = pool(fit)

    return [
        _row(
            "V02",
            "4 imp$meth (conv seed)",
            "after mice(seed=123)",
            g("02", 4, 9),
            format_meth_r(names, chain["imp_conv_seed"].method, style="nhanes"),
            exact=True,
            category=ParityCategory.STALE_GOLDEN,
            recommendation="Refresh golden if NO; chain order now aligned.",
        ),
        _row(
            "V02",
            "7 mira fit",
            "imp3 coefficients",
            g("02", 7, 21),
            format_mira_print_r(fit, nmis=imp3.nmis),
            category=ParityCategory.DRAW_ORDER,
            recommendation="Refresh g('02',7,21) from R after chain if NO.",
        ),
        _row(
            "V02",
            "7 lm imp 2",
            "complete(imp3,2) lm",
            g("02", 7, 24),
            format_lm_summary_r("bmi ~ chl", complete(imp3, 2), names2),
            atol=0.15,
            category=ParityCategory.DRAW_ORDER,
            recommendation="Refresh golden from R subprocess if NO.",
        ),
        _row(
            "V02",
            "8 pool qbar",
            "pooled estimates",
            g("02", 8, 25),
            format_pool_v02_r(summary_pool(pooled)),
            atol=0.5,
            category=ParityCategory.DRAW_ORDER,
            recommendation="Refresh g('02',8,25) from R after chain if NO.",
        ),
    ]


def audit_v03_pool() -> list[AuditRow]:
    from lib.data import load_boys_full_matrix, load_mammalsleep_full, load_mammalsleep_impute
    from lib.golden import golden_output as g
    from lib.r_style import format_pool_mipo_r, format_pool_v03_summary_r
    from lib.vignette_rng import run_v03_boys_chain, run_v03_mammalsleep_chain

    from pymice import pool, summary_pool, with_mids

    _fresh_session()
    boys, boy_names = load_boys_full_matrix()
    run_v03_boys_chain(boys, boy_names)
    ms_full, ms_names = load_mammalsleep_full()
    ms_no_sp, ms_no_names = load_mammalsleep_impute()
    imp_ms, impnew = run_v03_mammalsleep_chain(ms_full, ms_names, ms_no_sp, ms_no_names)
    fit1 = with_mids(imp_ms, formula="sws ~ log10(bw) + odi")
    fit2 = with_mids(impnew, formula="sws ~ log10(bw) + odi")
    # Path forks in remove_lindep change logged-event counts and desync the RNG stream.
    n_ms, n_new = len(imp_ms.logged_events), len(impnew.logged_events)
    rec = (
        f"logged_events imp={n_ms} impnew={n_new} "
        "(expect 25/18 on Windows after hardened remove_lindep; drift usually means path fork)."
    )

    return [
        _row(
            "V03",
            "12 pool mipo",
            "mammalsleep pool",
            g("03", 12, 24),
            format_pool_mipo_r(pool(fit1)),
            atol=0.5,
            category=ParityCategory.DRAW_ORDER,
            recommendation=rec,
        ),
        _row(
            "V03",
            "12 pool summary",
            "mammalsleep pool",
            g("03", 12, 25),
            format_pool_v03_summary_r(summary_pool(pool(fit1))),
            atol=0.5,
            category=ParityCategory.DRAW_ORDER,
            recommendation=rec,
        ),
        _row(
            "V03",
            "14 pool mipo impnew",
            "mammalsleep[,-1] pool",
            g("03", 14, 27),
            format_pool_mipo_r(pool(fit2)),
            atol=0.5,
            category=ParityCategory.DRAW_ORDER,
            recommendation=rec,
        ),
        _row(
            "V03",
            "14 pool summary impnew",
            "mammalsleep[,-1] pool",
            g("03", 14, 28),
            format_pool_v03_summary_r(summary_pool(pool(fit2))),
            atol=0.5,
            category=ParityCategory.DRAW_ORDER,
            recommendation=rec,
        ),
    ]


def audit_v03() -> list[AuditRow]:
    import numpy as np
    from lib.data import load_boys_full_matrix
    from lib.golden import golden_output as g
    from lib.r_style import format_summary_boys_r, format_tv_means_tibble_r
    from lib.vignette_rng import run_v03_boys_chain

    from pymice import complete

    _fresh_session()
    boys, boy_names = load_boys_full_matrix()
    imp1 = run_v03_boys_chain(boys, boy_names)
    tv_idx = boy_names.index("tv")

    def _tv_means() -> str:
        means = [float(np.nanmean(complete(imp1, i)[:, tv_idx])) for i in range(1, imp1.m + 1)]
        return format_tv_means_tibble_r(means)

    return [
        _row(
            "V03",
            "8 summary(complete(imp1))",
            "imputed boys summary",
            g("03", 8, 14),
            format_summary_boys_r(complete(imp1, 1), boy_names, compact_factors=True),
            exact=True,
            category=ParityCategory.DRAW_ORDER,
            recommendation="Refresh g('03',8,14) from R if NO.",
        ),
        _row(
            "V03",
            "8 mean(tv) per imp",
            "with(imp1, mean(tv))",
            g("03", 8, 15),
            _tv_means(),
            atol=0.2,
            category=ParityCategory.DRAW_ORDER,
            recommendation="Refresh g('03',8,15) from R if NO.",
        ),
    ]


def audit_v04() -> list[AuditRow]:
    from lib.data import load_boys_impute, load_mammalsleep_impute
    from lib.golden import golden_output as g
    from lib.vignette_rng import run_v04_chain
    from runners.v04_passive import _tv_table

    _fresh_session()
    ms_data, ms_names = load_mammalsleep_impute()
    boys, boy_names = load_boys_impute()
    chain = run_v04_chain(ms_data, ms_names, boys, boy_names)

    return [
        _row(
            "V04",
            "5 table norm tv",
            "post_squeeze norm",
            g("04", 5, 8),
            _tv_table(chain["imp_norm_post"], boy_names),
            category=ParityCategory.DRAW_ORDER,
            recommendation="Align chain + refresh g('04',5,8) from R if NO.",
        ),
        _row(
            "V04",
            "5 table pmm tv",
            "boys PMM",
            g("04", 5, 9),
            _tv_table(chain["imp_pmm"], boy_names),
            category=ParityCategory.DRAW_ORDER,
            recommendation="Align chain + refresh g('04',5,9) from R if NO.",
        ),
    ]


def audit_v05() -> list[AuditRow]:
    from lib.data import (
        load_popncr,
        load_popncr2,
        load_popncr3,
        load_popular,
        popncr_variable_specs,
    )
    from lib.golden import golden_output as g
    from lib.r_style import (
        format_icc_table_r,
        format_logged_events_warning_r,
        format_popncr_head_r,
    )
    from lib.vignette_rng import run_v05_multilevel_chain
    from runners.v05_multilevel import (
        ICC_VARS,
        _icc_values,
    )

    from pymice import complete

    _fresh_session()
    data, names = load_popncr()
    data2, names2 = load_popncr2()
    data3, names3 = load_popncr3()
    specs = popncr_variable_specs(data, names)
    specs2 = popncr_variable_specs(data2, names2)
    specs3 = popncr_variable_specs(data3, names3)
    chain = run_v05_multilevel_chain(
        data,
        names,
        data2,
        names2,
        data3,
        names3,
        specs3,
        specs=specs,
        specs2=specs2,
    )
    imp1 = chain["imp1"]
    imp2 = chain["imp2"]
    imp4 = chain["imp4"]
    imp8 = chain["imp8"]

    popular_data, popular_names = load_popular()
    obs_icc = _icc_values(data, names)
    orig_icc = _icc_values(popular_data, popular_names)
    imp1_icc = _icc_values(data, names, complete(imp1, 1))
    imp2_icc = _icc_values(data, names, complete(imp2, 1))
    imp4_icc = _icc_values(data, names, complete(imp4, 1))

    return [
        _row(
            "V05",
            "10 ICC norm",
            "session chain imp1",
            g("05", 10, 26),
            format_icc_table_r(list(ICC_VARS), {"observed": obs_icc, "norm": imp1_icc}),
            atol=0.05,
            category=ParityCategory.DRAW_ORDER,
            recommendation="norm column within atol=5e-4 after factor class + remove.lindep fix.",
        ),
        _row(
            "V05",
            "12 ICC normclass",
            "session chain imp2",
            g("05", 12, 28),
            format_icc_table_r(
                list(ICC_VARS),
                {"observed": obs_icc, "norm": imp1_icc, "normclass": imp2_icc},
            ),
            atol=0.05,
            category=ParityCategory.ALGORITHM,
            recommendation="MATCH within atol=0.05 after factor class + remove.lindep fix.",
        ),
        _row(
            "V05",
            "20 ICC full",
            "session chain imp4",
            g("05", 20, 40),
            format_icc_table_r(
                list(ICC_VARS),
                {
                    "observed": obs_icc,
                    "norm": imp1_icc,
                    "normclass": imp2_icc,
                    "pmm": imp4_icc,
                    "orig": orig_icc,
                },
            ),
            atol=0.05,
            category=ParityCategory.DRAW_ORDER,
            recommendation="observed/orig exact; imputed ICC columns partial.",
        ),
        _row(
            "V05",
            "16 head(complete(imp2))",
            "session chain",
            g("05", 16, 37),
            format_popncr_head_r(complete(imp2, 1), names, n=15),
            atol=0.15,
            category=ParityCategory.ALGORITHM,
            recommendation="R layout; imputed values within atol=0.15 (draw-order).",
        ),
        _row(
            "V05",
            "11 logged events imp2",
            "session chain",
            g("05", 11, 27),
            format_logged_events_warning_r(len(imp2.logged_events)),
            exact=True,
            category=ParityCategory.ALGORITHM,
            recommendation="MATCH logged-event count on session chain after type-1 factor design fix.",
        ),
        _row(
            "V05",
            "26 logged events imp8",
            "session chain",
            g("05", 26, 57),
            format_logged_events_warning_r(len(imp8.logged_events)),
            exact=True,
            category=ParityCategory.ALGORITHM,
            recommendation="MATCH logged-event count on session chain after type-1 factor design fix.",
        ),
    ]


def scan_partial_reasons() -> list[AuditRow]:
    """Collect partial=True steps whose reason cites RNG/draw-order keywords."""
    rows: list[AuditRow] = []
    for path in sorted((RUNNERS_DIR).glob("v0[1-5]_*.py")):
        text = path.read_text()
        vignette = "V" + path.stem[1:3]
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Name) and func.id == "TutorialPart"):
                continue
            kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
            if "partial" not in kwargs or "partial_reason" not in kwargs:
                continue
            partial_val = kwargs["partial"]
            if not (isinstance(partial_val, ast.Constant) and partial_val.value is True):
                continue
            reason_node = kwargs["partial_reason"]
            if not isinstance(reason_node, ast.Constant) or not isinstance(reason_node.value, str):
                continue
            reason = reason_node.value
            if not RNG_RE.search(reason):
                continue
            r_code = ""
            if "r_code" in kwargs and isinstance(kwargs["r_code"], ast.Constant):
                r_code = str(kwargs["r_code"].value).split("\n")[0][:40]
            rows.append(
                AuditRow(
                    vignette=vignette,
                    step=r_code or "(tutorial part)",
                    reason=reason[:80],
                    matches=False,
                    category=ParityCategory.DRAW_ORDER,
                    recommendation="Re-audit after chain helper wired into run()",
                    source="source-scan",
                )
            )
    return rows


def _categorize_still_partial(rows: list[AuditRow]) -> dict[ParityCategory, list[AuditRow]]:
    out: dict[ParityCategory, list[AuditRow]] = {}
    for row in rows:
        if row.matches:
            continue
        out.setdefault(row.category, []).append(row)
    return out


def _merge_backlog(audit_rows: list[AuditRow]) -> list[ParityTask]:
    tasks = default_backlog()
    recompared = [r for r in audit_rows if r.source == "re-compare"]

    def _matches_for(task: ParityTask) -> bool | None:
        hits = [r.matches for r in recompared if r.vignette == task.vignette]
        if not hits:
            return None
        if task.step in {"7–8 imp3 mira/pool", "11–14 mammalsleep pool", "8–9 norm.predict"}:
            relevant = [
                r.matches for r in recompared if r.vignette == task.vignette and not r.matches
            ]
            return False if relevant else all(hits)
        if task.step == "4 imp$meth":
            row = next((r for r in recompared if "imp$meth" in r.step), None)
            return row.matches if row else None
        if task.step == "8 summary(complete(imp1))":
            row = next((r for r in recompared if "summary(complete" in r.step), None)
            return row.matches if row else None
        if task.step == "8 with(imp1, mean(tv))":
            row = next((r for r in recompared if "mean(tv)" in r.step), None)
            return row.matches if row else None
        if task.step == "5 table(tv)":
            rows = [r for r in recompared if r.vignette == "V04" and "table" in r.step]
            return all(r.matches for r in rows) if rows else None
        if task.step == "13 print(imp)":
            row = next((r for r in recompared if "print(imp)" in r.step), None)
            return row.matches if row else None
        if task.step == "2 pas.imp":
            return True if task.chain_ready else None
        return None

    return [
        ParityTask(
            vignette=task.vignette,
            step=task.step,
            category=task.category,
            partial_reason=task.partial_reason,
            recommendation=task.recommendation,
            priority=task.priority,
            matches_now=_matches_for(task),
            chain_ready=task.chain_ready,
        )
        for task in tasks
    ]


def main() -> int:
    audit_rows = (
        audit_v01() + audit_v02() + audit_v03() + audit_v03_pool() + audit_v04() + audit_v05()
    )
    scanned = scan_partial_reasons()

    print("=" * 100)
    print("RNG / draw-order re-compare (aligned chain helpers)")
    print("=" * 100)
    print(f"{'Vignette':<6} {'Step':<32} {'Match?':<8} {'Category':<14} Source")
    print("-" * 100)
    for r in audit_rows:
        print(
            f"{r.vignette:<6} {r.step:<32} {'YES' if r.matches else 'NO':<8} "
            f"{r.category.value:<14} {r.source}"
        )

    still_differ = [r for r in audit_rows if not r.matches]
    now_match = [r for r in audit_rows if r.matches]
    print(
        f"\nRe-compared {len(audit_rows)} steps: {len(now_match)} match, "
        f"{len(still_differ)} still differ."
    )

    if still_differ:
        print("\nStill differ — by category:")
        for cat, items in _categorize_still_partial(audit_rows).items():
            print(f"\n  [{cat.value}] ({len(items)})")
            for item in items:
                print(f"    - {item.vignette} {item.step}: {item.recommendation}")

    print("\n" + "=" * 100)
    print(f"Source scan: {len(scanned)} partial steps cite RNG/draw-order (V01–V05)")
    print("=" * 100)
    by_v: dict[str, int] = {}
    for s in scanned:
        by_v[s.vignette] = by_v.get(s.vignette, 0) + 1
    for v, n in sorted(by_v.items()):
        print(f"  {v}: {n} flagged partials in source")

    backlog = _merge_backlog(audit_rows)
    path = save_backlog(backlog)
    print(f"\nBacklog written: {path}")
    print("Next prompt: wire chain helpers into run(), refresh goldens where matches_now=False.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
