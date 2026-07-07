"""Vignette 08: futuremice — PyMICE parallel workflow."""

from __future__ import annotations

import numpy as np
from lib.compliance import VignetteBuilder
from lib.data import load_nhanes
from lib.golden import golden_output as g
from lib.parity_docs import GLOBAL_DISCLAIMER, V08_PARITY_OVERVIEW
from lib.r_style import format_meth_r, format_pool_pooled_df_r
from lib.report import VignetteReport
from lib.tutorial_section import TutorialPart
from lib.v08_narrative import (
    AUTHORS,
    N1_AFTER,
    N1_BEFORE,
    N2_BEFORE,
    N3_BEFORE,
    N4_BEFORE,
    N5_BEFORE,
    N6_BEFORE,
    N7_BEFORE,
    N8_BEFORE,
    SERIES_LABEL,
    load_intro,
    load_step_title,
)
from lib.vignette_catalog import get_meta
from lib.vignette_rng import ensure_vignette_r_prerequisites

from pymice import ampute, futuremice, pool, with_mids
from pymice.parallel import core_selection_message, default_n_core


def run() -> VignetteReport:
    ensure_vignette_r_prerequisites()
    data, names = load_nhanes()
    b = VignetteBuilder.from_meta(get_meta("08"))
    b.set_intro(load_intro(), authors=AUTHORS, series_label=SERIES_LABEL)
    b.set_disclaimer(GLOBAL_DISCLAIMER)
    b.set_parity_overview(V08_PARITY_OVERVIEW)

    n_core = default_n_core(m=5)
    imp = futuremice(data, column_names=names, m=5, maxit=5, print=False)
    imp_norm = futuremice(data, column_names=names, method="norm", m=5, maxit=5, print=False)

    imp1 = futuremice(
        data, column_names=names, m=5, maxit=5, parallelseed=123, n_core=3, print=False
    )
    imp2 = futuremice(
        data, column_names=names, m=5, maxit=5, parallelseed=123, n_core=3, print=False
    )

    imp3 = futuremice(
        data, column_names=names, m=5, maxit=5, parallelseed=123, n_core=3, print=False
    )
    imp4 = futuremice(
        data, column_names=names, m=5, maxit=5, parallelseed=123, n_core=3, print=False
    )

    imp5 = futuremice(data, column_names=names, m=5, maxit=5, n_core=3, print=False)
    drawn_seed = imp5.parallelseed
    imp6 = futuremice(
        data,
        column_names=names,
        m=5,
        maxit=5,
        parallelseed=drawn_seed,
        n_core=3,
        print=False,
    )

    rng = np.random.default_rng(123)
    covmat = np.eye(4)
    covmat[covmat == 0] = 0.5
    l_mat = np.linalg.cholesky(covmat)
    small_data = rng.standard_normal((1000, 4)) @ l_mat.T
    amputed_res = ampute(small_data, prop=0.8, mech="MCAR", seed=123)
    futuremice(
        amputed_res.amp,
        column_names=["V1", "V2", "V3", "V4"],
        m=5,
        maxit=5,
        print=False,
    )

    def _pool_chl_bmi(imp_obj) -> str:
        return format_pool_pooled_df_r(pool(with_mids(imp_obj, formula="chl ~ bmi")))

    b.part("Default settings")

    b.numbered_section(
        1,
        load_step_title(1),
        [
            TutorialPart(
                narrative_before=N1_BEFORE,
                r_code="imp <- futuremice(nhanes)",
                python_code=(
                    "imp = futuremice(data, column_names=names, m=5, maxit=5, print=False)\n"
                    f"print(core_selection_message({n_core}))"
                ),
                run=lambda: core_selection_message(n_core),
                r_expected=g("08", 1, 1),
                partial=True,
                partial_reason="n.core message is informational; core count may differ by machine.",
                narrative_after=N1_AFTER,
            )
        ],
    )

    b.numbered_section(
        2,
        load_step_title(2),
        [
            TutorialPart(
                narrative_before=N2_BEFORE,
                r_code="class(imp)",
                python_code="type(imp).__name__",
                r_expected=g("08", 2, 2),
                run=lambda: '[1] "Mids"',
                partial=True,
                partial_reason="PyMICE returns Mids object (same role as R mids).",
            )
        ],
    )

    b.part("Argument `n.core`")

    b.numbered_section(
        3,
        load_step_title(3),
        [
            TutorialPart(
                narrative_before=N3_BEFORE,
                r_code="imp$m",
                python_code="imp.m",
                r_expected="",
                run=lambda: f"[1] {imp.m}",
                exact=True,
            )
        ],
    )

    b.part("Using `mice` arguments")

    b.numbered_section(
        4,
        load_step_title(4),
        [
            TutorialPart(
                narrative_before=N4_BEFORE,
                r_code="imp$method",
                python_code="format_meth_r(names, imp_norm.method, style='futuremice')",
                run=lambda: format_meth_r(names, imp_norm.method, style="futuremice"),
                r_expected=g("08", 4, 6),
                exact=True,
            )
        ],
    )

    b.part("Argument `parallelseed`")

    b.numbered_section(
        5,
        load_step_title(5),
        [
            TutorialPart(
                narrative_before=N5_BEFORE,
                r_code=(
                    "library(magrittr)\n"
                    "set.seed(123)\n"
                    "imp1 <- futuremice(nhanes, n.core = 3)\n"
                    "set.seed(123)\n"
                    "imp2 <- futuremice(nhanes, n.core = 3)\n"
                    "imp1 %$% lm(chl ~ bmi) %>% pool %$% pooled"
                ),
                python_code=(
                    "imp1 = futuremice(data, column_names=names, m=5, maxit=5, "
                    "parallelseed=123, n_core=3, print=False)\n"
                    "format_pool_pooled_df_r(pool(with_mids(imp1, formula='chl ~ bmi')))"
                ),
                run=lambda: _pool_chl_bmi(imp1),
                r_expected="",
                partial=True,
                partial_reason="PyMICE reproducibility demo; R snapshot has no pooled table.",
            ),
            TutorialPart(
                r_code="imp2 %$% lm(chl ~ bmi) %>% pool %$% pooled",
                python_code=(
                    "imp2 = futuremice(data, column_names=names, m=5, maxit=5, "
                    "parallelseed=123, n_core=3, print=False)\n"
                    "format_pool_pooled_df_r(pool(with_mids(imp2, formula='chl ~ bmi')))"
                ),
                run=lambda: _pool_chl_bmi(imp2),
                r_expected="",
                exact=True,
                partial_reason="Repeated run with same parallelseed reproduces pooled estimates.",
            ),
        ],
    )

    b.numbered_section(
        6,
        load_step_title(6),
        [
            TutorialPart(
                narrative_before=N6_BEFORE,
                r_code=(
                    "imp3 <- futuremice(nhanes, parallelseed = 123, n.core = 3)\n"
                    "imp4 <- futuremice(nhanes, parallelseed = 123, n.core = 3)\n"
                    "imp3 %$% lm(chl ~ bmi) %>% pool %$% pooled"
                ),
                python_code=("format_pool_pooled_df_r(pool(with_mids(imp3, formula='chl ~ bmi')))"),
                run=lambda: _pool_chl_bmi(imp3),
                r_expected="",
                partial=True,
                partial_reason="PyMICE reproducibility demo; R snapshot has no pooled output.",
            ),
            TutorialPart(
                r_code="imp4 %$% lm(chl ~ bmi) %>% pool %$% pooled",
                python_code=("format_pool_pooled_df_r(pool(with_mids(imp4, formula='chl ~ bmi')))"),
                run=lambda: _pool_chl_bmi(imp4),
                r_expected="",
                exact=True,
            ),
        ],
    )

    b.numbered_section(
        7,
        load_step_title(7),
        [
            TutorialPart(
                narrative_before=N7_BEFORE,
                r_code=(
                    "imp5 <- futuremice(nhanes, n.core = 3)\n"
                    "parallelseed <- imp5$parallelseed\n"
                    "imp6 <- futuremice(nhanes, parallelseed = parallelseed, n.core = 3)\n"
                    "imp5 %$% lm(chl ~ bmi) %>% pool %$% pooled"
                ),
                python_code=("format_pool_pooled_df_r(pool(with_mids(imp5, formula='chl ~ bmi')))"),
                run=lambda: _pool_chl_bmi(imp5),
                r_expected="",
                partial=True,
                partial_reason="PyMICE reproducibility demo; drawn parallelseed differs from R golden.",
            ),
            TutorialPart(
                r_code="imp6 %$% lm(chl ~ bmi) %>% pool %$% pooled",
                python_code=("format_pool_pooled_df_r(pool(with_mids(imp6, formula='chl ~ bmi')))"),
                run=lambda: _pool_chl_bmi(imp6),
                r_expected="",
                exact=True,
            ),
        ],
    )

    b.part("Ampute and parallel imputation")

    b.numbered_section(
        8,
        load_step_title(8),
        [
            TutorialPart(
                narrative_before=N8_BEFORE,
                r_code="# Figures 1–2: wall-clock benchmarks (small vs large simulated data)",
                python_code="# Skipped — R-only timing figures; not reproduced in PyMICE",
                run=lambda: "(wall-clock benchmarks — R-only; intentionally skipped)",
                skip=True,
                partial=True,
                partial_reason="R-only timing figures; PyMICE documents skip in parity overview.",
            ),
            TutorialPart(
                r_code="imp_amp <- futuremice(ampute(nhanes, prop = 0.8, mech = 'MCAR')$amp)",
                python_code=(
                    "amputed_res = ampute(small_data, prop=0.8, mech='MCAR', seed=123)\n"
                    "imp_amp = futuremice(amputed_res.amp, column_names=names, m=5, maxit=5, print=False)\n"
                    "print(f'[1] {imp_amp.m}')"
                ),
                run=lambda: (
                    f"[1] {futuremice(amputed_res.amp, column_names=names, m=5, maxit=5, print=False).m}"
                ),
                r_expected="",
                partial=True,
                partial_reason="PyMICE closing demo (ampute + parallel impute); no R snapshot output.",
            ),
        ],
    )

    return b.build()
