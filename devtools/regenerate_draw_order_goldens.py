#!/usr/bin/env python3
"""Refresh golden_outputs.json entries for draw-order-aligned V02–V04 steps."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

DEVTOOLS = Path(__file__).resolve().parent
ROOT = DEVTOOLS.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(DEVTOOLS))

from lib.golden_store import update_golden_key  # noqa: E402


def _update(vignette_dir: str, key: str, r_output: str) -> None:
    update_golden_key(vignette_dir, key, r_output)


def main() -> int:
    from lib.data import (
        load_boys_full_matrix,
        load_boys_impute,
        load_mammalsleep_full,
        load_mammalsleep_impute,
        load_nhanes,
        load_nhanes2,
    )
    from lib.r_style import (
        format_lm_summary_r,
        format_logged_events_warning_r,
        format_mira_print_r,
        format_pool_mipo_r,
        format_pool_v02_r,
        format_pool_v03_summary_r,
        format_summary_boys_r,
        format_tv_means_tibble_r,
    )
    from lib.vignette_rng import (
        ensure_vignette_r_prerequisites,
        run_v02_mice_chain,
        run_v03_boys_chain,
        run_v03_mammalsleep_chain,
        run_v04_chain,
        start_vignette_rng_session,
    )
    from runners.v02_convergence_pooling import NHANES2_SPECS
    from runners.v04_passive import _tv_table

    from pymice import complete, pool, summary_pool, with_mids
    from pymice.rng import RSession

    ensure_vignette_r_prerequisites()

    # --- V02 ---
    RSession.close()
    start_vignette_rng_session(123)
    data, names = load_nhanes()
    data2, names2 = load_nhanes2()
    chain02 = run_v02_mice_chain(data, names, data2, names2, NHANES2_SPECS)
    imp3 = chain02["imp3"]
    fit = with_mids(imp3, formula="bmi ~ chl")
    pooled = pool(fit)

    _update(
        "02_convergence_and_pooling",
        "7.21",
        format_mira_print_r(fit, nmis=imp3.nmis),
    )
    _update(
        "02_convergence_and_pooling",
        "7.24",
        format_lm_summary_r("bmi ~ chl", complete(imp3, 2), names2),
    )
    _update(
        "02_convergence_and_pooling",
        "8.25",
        format_pool_v02_r(summary_pool(pooled)),
    )

    # --- V03 boys ---
    RSession.close()
    start_vignette_rng_session(123)
    boys, boy_names = load_boys_full_matrix()
    imp1 = run_v03_boys_chain(boys, boy_names)
    tv_idx = boy_names.index("tv")

    _update(
        "03_missingness_inspection",
        "8.14",
        format_summary_boys_r(complete(imp1, 1), boy_names, compact_factors=True),
    )
    means = [float(np.nanmean(complete(imp1, i)[:, tv_idx])) for i in range(1, imp1.m + 1)]
    _update(
        "03_missingness_inspection",
        "8.15",
        format_tv_means_tibble_r(means),
    )

    # --- V03 mammalsleep (continues session after boys) ---
    ms_full, ms_names = load_mammalsleep_full()
    ms_no_sp, ms_no_names = load_mammalsleep_impute()
    imp_ms, impnew = run_v03_mammalsleep_chain(ms_full, ms_names, ms_no_sp, ms_no_names)
    fit1 = with_mids(imp_ms, formula="sws ~ log10(bw) + odi")
    fit2 = with_mids(impnew, formula="sws ~ log10(bw) + odi")
    pooled1 = pool(fit1)
    pooled2 = pool(fit2)

    _update(
        "03_missingness_inspection",
        "10.21",
        format_logged_events_warning_r(len(imp_ms.logged_events)),
    )
    _update(
        "03_missingness_inspection",
        "13.26",
        format_logged_events_warning_r(len(impnew.logged_events)),
    )
    _update("03_missingness_inspection", "12.24", format_pool_mipo_r(pooled1))
    _update(
        "03_missingness_inspection",
        "12.25",
        format_pool_v03_summary_r(summary_pool(pooled1)),
    )
    _update("03_missingness_inspection", "14.27", format_pool_mipo_r(pooled2))
    _update(
        "03_missingness_inspection",
        "14.28",
        format_pool_v03_summary_r(summary_pool(pooled2)),
    )

    # --- V04 ---
    RSession.close()
    start_vignette_rng_session(123)
    ms_data, ms_names = load_mammalsleep_impute()
    boys_i, boy_names = load_boys_impute()
    chain04 = run_v04_chain(ms_data, ms_names, boys_i, boy_names)

    _update(
        "04_passive_post_processing",
        "5.8",
        _tv_table(chain04["imp_norm_post"], boy_names),
    )
    _update(
        "04_passive_post_processing",
        "5.9",
        _tv_table(chain04["imp_pmm"], boy_names),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
