#!/usr/bin/env python3
"""Refresh V06 golden outputs for δ-chain Cox/pool and mammalsleep qbar steps."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

DEVTOOLS = Path(__file__).resolve().parent
ROOT = DEVTOOLS.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(DEVTOOLS))

from lib.golden_store import update_golden_key  # noqa: E402

DELTA = [0, -5, -10, -15, -20]
DELTA_MS = [8, 6, 4, 2, 0, -2, -4, -6, -8]


def _update(vignette_dir: str, key: str, r_output: str) -> None:
    update_golden_key(vignette_dir, key, r_output)


def main() -> int:
    import numpy as np
    from lib.data import load_leiden, load_mammalsleep_impute
    from lib.r_style import (
        format_cox_pars_table_r,
        format_delta_qbar_table,
        format_mira_cox_v06_r,
        format_pool_cox_summary_r,
    )
    from lib.vignette_rng import (
        ensure_vignette_r_prerequisites,
        run_v06_leiden_delta_chain,
        run_v06_mammalsleep_delta_chain,
        start_vignette_rng_session,
    )

    from pymice import pool, summary_pool, with_mids
    from pymice.analysis.survival import leiden_coxph
    from pymice.rng import RSession

    ensure_vignette_r_prerequisites()
    RSession.close()
    start_vignette_rng_session(123)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        data, names = load_leiden()
        imp_all = run_v06_leiden_delta_chain(data, names)

        cox_fits = [
            with_mids(imp, expr=lambda completed, cols=names: leiden_coxph(completed, cols))
            for imp in imp_all
        ]
        fit3 = cox_fits[2]
        pooled_fit1_summary = summary_pool(pool(cox_fits[0]))
        cox_pars_rows: list[list[float]] = []
        for mira in cox_fits:
            summ = summary_pool(pool(mira))
            exp_vals = [float(np.exp(float(row["estimate"]))) for row in summ]
            cox_pars_rows.append([exp_vals[0], exp_vals[1], exp_vals[4]])

        ms_data, ms_names = load_mammalsleep_impute()
        ms_delta_qbars = run_v06_mammalsleep_delta_chain(ms_data, ms_names)

    _update(
        "06_sensitivity_analysis",
        "0.20",
        format_mira_cox_v06_r(
            fit3,
            nmis=imp_all[2].nmis,
            imp_label="imp.all[[3]]",
            seed_line="    seed = i)",
        ),
    )
    _update(
        "06_sensitivity_analysis",
        "0.21",
        format_pool_cox_summary_r(pooled_fit1_summary),
    )
    _update(
        "06_sensitivity_analysis",
        "0.22",
        format_cox_pars_table_r(DELTA, cox_pars_rows),
    )
    _update(
        "06_sensitivity_analysis",
        "0.24",
        format_delta_qbar_table(DELTA_MS, ms_delta_qbars),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
