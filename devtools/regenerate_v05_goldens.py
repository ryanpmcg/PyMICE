#!/usr/bin/env python3
"""Refresh V05 golden outputs that depend on the popNCR session chain."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

DEVTOOLS = Path(__file__).resolve().parent
ROOT = DEVTOOLS.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(DEVTOOLS))

from lib.golden_store import update_golden_key  # noqa: E402


def _update(vignette_dir: str, key: str, r_output: str) -> None:
    update_golden_key(vignette_dir, key, r_output)


def main() -> int:
    from lib.data import (
        load_popncr,
        load_popncr2,
        load_popncr3,
        load_popular,
        popncr_variable_specs,
    )
    from lib.r_style import format_icc_table_r
    from lib.summary_format import format_popncr_head_r
    from lib.vignette_rng import (
        ensure_vignette_r_prerequisites,
        run_v05_multilevel_chain,
        start_vignette_rng_session,
    )
    from runners.v05_multilevel import ICC_VARS, _icc_values

    from pymice import complete
    from pymice.rng import RSession

    ensure_vignette_r_prerequisites()
    RSession.close()
    start_vignette_rng_session(123)
    data, names = load_popncr()
    data2, names2 = load_popncr2()
    data3, names3 = load_popncr3()
    specs = popncr_variable_specs(data, names)
    specs2 = popncr_variable_specs(data2, names2)
    specs3 = popncr_variable_specs(data3, names3)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
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
    popular_data, popular_names = load_popular()
    obs_icc = _icc_values(data, names)
    imp1_icc = _icc_values(data, names, complete(imp1, 1))
    imp2_icc = _icc_values(data, names, complete(imp2, 1))
    imp4_icc = _icc_values(data, names, complete(imp4, 1))
    orig_icc = _icc_values(popular_data, popular_names)

    _update(
        "05_multilevel_data",
        "10.26",
        format_icc_table_r(list(ICC_VARS), {"observed": obs_icc, "norm": imp1_icc}),
    )
    _update(
        "05_multilevel_data",
        "12.28",
        format_icc_table_r(
            list(ICC_VARS),
            {"observed": obs_icc, "norm": imp1_icc, "normclass": imp2_icc},
        ),
    )
    _update(
        "05_multilevel_data",
        "20.40",
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
    )
    _update(
        "05_multilevel_data",
        "16.37",
        format_popncr_head_r(complete(imp2, 1), names, n=15),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
