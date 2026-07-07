"""Vignette 02: Convergence and pooling — mirrors R tutorial (steps 1–8)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from lib.compliance import VignetteBuilder
from lib.data import load_nhanes, load_nhanes2
from lib.golden import golden_output as g
from lib.parity_docs import GLOBAL_DISCLAIMER, V02_PARITY_OVERVIEW
from lib.r_style import (
    R_METHODS_MICE,
    R_STR_NHANES2,
    format_lm_summary_r,
    format_meth_r,
    format_mira_print_r,
    format_pool_v02_r,
    format_predictor_matrix,
    format_summary_nhanes2_r,
)
from lib.report import VignetteReport
from lib.tutorial_section import TutorialPart
from lib.v02_narrative import (
    AUTHORS,
    N1_BEFORE,
    N2_AFTER_INI,
    N2_AFTER_MOD,
    N2_AFTER_PRED,
    N2_AFTER_QUICK,
    N2_BEFORE_PRED,
    N2_BEFORE_QUICK,
    N3_AFTER_PLOT,
    N3_AFTER_SEED,
    N3_BEFORE,
    N3_BEFORE_SEED,
    N4_AFTER_METH,
    N4_AFTER_METH2,
    N4_AFTER_METHODS,
    N4_AFTER_NORM,
    N4_AFTER_STR,
    N4_BEFORE_METH,
    N4_BEFORE_METHODS,
    N4_BEFORE_PLOT,
    N4_BEFORE_STR,
    N5_BEFORE,
    N6_AFTER_STRIP,
    N6_AFTER_STRIP2,
    N6_BEFORE,
    N6_BEFORE_STRIP2,
    N7_AFTER_FIT,
    N7_BEFORE_A2,
    N7_BEFORE_LS,
    N7_FORMULA,
    N8_AFTER,
    N8_AFTER_SCALAR,
    N8_BEFORE,
    SERIES_LABEL,
    load_intro,
    load_step_title,
)
from lib.vignette_catalog import get_meta
from lib.vignette_rng import (
    ensure_vignette_r_prerequisites,
    run_v02_mice_chain,
)
from lib.viz import save_figure

from pymice import complete, continue_imputation, pool, quickpred, summary_pool, with_mids
from pymice.diagnostics.plots import plot_mids, plot_stripplot
from pymice.types import VariableKind, VariableSpec

R_SETUP = ""
R_MICE_M3 = ""
R_MICE_PRED = ""
R_MICE_SEED = ""
R_MICE_METH = ""

ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"

NHANES2_SPECS = [
    VariableSpec("age", VariableKind.UNORDERED, levels=(1.0, 2.0, 3.0)),
    VariableSpec("bmi", VariableKind.NUMERIC),
    VariableSpec("hyp", VariableKind.BINARY, levels=(1.0, 2.0)),
    VariableSpec("chl", VariableKind.NUMERIC),
]


def _stripplot_panel(mids, variables: list[str]):
    fig, axes = plt.subplots(1, len(variables), figsize=(4 * len(variables), 4), squeeze=False)
    for ax, var in zip(axes[0], variables, strict=True):
        plot_stripplot(mids, var, ax=ax)
    fig.tight_layout()
    return fig


def run() -> VignetteReport:
    ensure_vignette_r_prerequisites()
    data, names = load_nhanes()
    data2, names2 = load_nhanes2()
    b = VignetteBuilder.from_meta(get_meta("02"))
    b.set_intro(load_intro(), authors=AUTHORS, series_label=SERIES_LABEL)
    b.set_disclaimer(GLOBAL_DISCLAIMER)
    b.set_parity_overview(V02_PARITY_OVERVIEW)
    ASSETS.mkdir(parents=True, exist_ok=True)

    chain = run_v02_mice_chain(data, names, data2, names2, NHANES2_SPECS)
    imp_m3 = chain["imp_m3"]
    ini0 = chain["ini0"]
    pred = ini0.predictor_matrix.copy()
    pred_mod = pred.copy()
    pred_mod[:, names.index("hyp")] = 0
    pred_quick = quickpred(data, mincor=0.3, column_names=names)
    imp_conv = chain["imp_conv"]
    imp_conv_seed = chain["imp_conv_seed"]
    imp2 = chain["imp2"]
    ini2 = chain["ini2"]
    imp3 = chain["imp3"]
    meth = dict(ini2.method)
    meth["bmi"] = "norm"
    imp40 = continue_imputation(imp3, maxit=35, print=False)

    fit = with_mids(imp3, formula="bmi ~ chl")
    pooled = pool(fit)

    trace_nhanes = save_figure(
        plot_mids(imp_conv, variables=["bmi", "hyp", "chl"]),
        ASSETS,
        "v02_trace_nhanes.png",
    )
    trace_nhanes2 = save_figure(
        plot_mids(imp3, variables=["bmi", "hyp", "chl"]),
        ASSETS,
        "v02_trace_nhanes2.png",
    )
    trace_40 = save_figure(
        plot_mids(imp40, variables=["bmi", "hyp", "chl"]),
        ASSETS,
        "v02_trace_40.png",
    )
    strip_chl = save_figure(plot_stripplot(imp3, "chl"), ASSETS, "v02_stripplot_chl.png")
    strip_multi = save_figure(
        _stripplot_panel(imp3, ["chl", "bmi"]), ASSETS, "v02_stripplot_multi.png"
    )

    def _pool_out() -> str:
        return format_pool_v02_r(summary_pool(pooled))

    # --- Steps 1–6 ---
    b.numbered_section(
        1,
        load_step_title(1),
        [
            TutorialPart(
                r_code="require(mice)\nrequire(lattice)\nset.seed(123)",
                r_expected=R_SETUP,
                python_code=(
                    "import numpy as np\n"
                    "from pymice import mice, pool, with_mids, summary_pool, quickpred, complete\n"
                    "from pymice.diagnostics.plots import plot_mids, plot_stripplot\n"
                    "from lib.data import load_nhanes, load_nhanes2\n"
                    "from lib.viz import save_figure\n"
                    "from lib.r_style import (\n"
                    "    format_meth_r,\n"
                    "    format_pool_print_r,\n"
                    "    format_pool_tibble_r,\n"
                    "    format_predictor_matrix,\n"
                    "    format_summary_r,\n"
                    "    format_mira_print_r,\n"
                    "    format_lm_summary_r,\n"
                    "    format_pool_v02_r\n"
                    ")"
                ),
                run=lambda: "(setup — no console output)",
                partial=True,
                partial_reason="Package load step; no R console output to compare.",
            ),
            TutorialPart(
                narrative_before=N1_BEFORE,
                r_code="imp <- mice(nhanes, m = 3, print=F)",
                r_expected=R_MICE_M3,
                python_code="imp_m3 = mice(data, column_names=names, m=3, maxit=5, seed=123, print_flag=False)",
                run=lambda: "(m = 3 imputation complete — no printed output in R vignette)",
                partial=True,
                partial_reason="Step creates `imp` object; R vignette prints no console output here.",
            ),
        ],
    )

    b.numbered_section(
        2,
        load_step_title(2),
        [
            TutorialPart(
                narrative_before=N2_BEFORE_PRED,
                r_code="imp$pred",
                python_code="print(format_predictor_matrix(names, imp_m3.predictor_matrix))",
                run=lambda: format_predictor_matrix(names, imp_m3.predictor_matrix),
                r_expected=g("02", 2, 2),
                exact=True,
                narrative_after=N2_AFTER_PRED,
            ),
            TutorialPart(
                r_code="ini <- mice(nhanes, maxit=0, print=F)\npred <- ini$pred\npred",
                python_code="print(format_predictor_matrix(names, ini0.predictor_matrix))",
                run=lambda: format_predictor_matrix(names, pred),
                r_expected=g("02", 2, 3),
                exact=True,
                narrative_after=N2_AFTER_INI,
            ),
            TutorialPart(
                r_code='pred[ ,"hyp"] <- 0\npred',
                python_code=(
                    "pred[:, names.index('hyp')] = 0\nprint(format_predictor_matrix(names, pred))"
                ),
                run=lambda: format_predictor_matrix(names, pred_mod),
                r_expected=g("02", 2, 4),
                exact=True,
                narrative_after=N2_AFTER_MOD,
            ),
            TutorialPart(
                r_code="imp <- mice(nhanes, pred=pred, print=F)",
                r_expected=R_MICE_PRED,
                python_code="mice(data, column_names=names, predictor_matrix=pred_mod, seed=123, print_flag=False)",
                run=lambda: "(imputation with custom predictor matrix — no printed output)",
                partial=True,
                partial_reason="R vignette shows code only; no console output to compare.",
            ),
            TutorialPart(
                narrative_before=N2_BEFORE_QUICK,
                r_code="ini <- mice(nhanes, pred=quickpred(nhanes, mincor=.3), print=F)\nini$pred",
                python_code="print(format_predictor_matrix(names, pred_quick))",
                run=lambda: format_predictor_matrix(names, pred_quick),
                r_expected=g("02", 2, 6),
                exact=True,
                narrative_after=N2_AFTER_QUICK,
            ),
        ],
    )

    b.numbered_section(
        3,
        load_step_title(3),
        [
            TutorialPart(
                narrative_before=N3_BEFORE,
                r_code="imp <- mice(nhanes, print=F)\nplot(imp)",
                r_expected=R_MICE_SEED,
                python_code=(
                    "fig = plot_mids(imp_conv, variables=['bmi', 'hyp', 'chl'])\n"
                    "save_figure(fig, ASSETS, 'v02_plot_mids.png')"
                ),
                is_plot=True,
                plot_note="Matplotlib trace plot (mean imputations per iteration).",
                narrative_after=N3_AFTER_PLOT,
            ),
            TutorialPart(
                narrative_before=N3_BEFORE_SEED,
                r_code="imp <- mice(nhanes, seed=123, print=F)",
                r_expected=R_MICE_SEED,
                python_code="imp_conv = mice(data, column_names=names, m=5, maxit=5, seed=123, print_flag=False)",
                run=lambda: "(reproducible imputation — no printed output)",
                partial=True,
                partial_reason="Seed argument demonstration; no console output in R vignette.",
                narrative_after=N3_AFTER_SEED,
            ),
        ],
        images=[trace_nhanes],
    )

    b.numbered_section(
        4,
        load_step_title(4),
        [
            TutorialPart(
                narrative_before=N4_BEFORE_METH,
                r_code="imp$meth",
                python_code="print(format_meth_r(names, imp_conv_seed.method, style='nhanes'))",
                run=lambda: format_meth_r(names, imp_conv_seed.method, style="nhanes"),
                r_expected=g("02", 4, 9),
                exact=True,
                narrative_after=N4_AFTER_METH,
            ),
            TutorialPart(
                r_code="summary(nhanes2)",
                r_expected=g("02", 4, 10),
                python_code="print(format_summary_nhanes2_r(data2, names2))",
                run=lambda: format_summary_nhanes2_r(data2, names2),
                exact=True,
            ),
            TutorialPart(
                narrative_before=N4_BEFORE_STR,
                r_code="str(nhanes2)",
                python_code="# str() layout — R factor labels vs numeric codes in PyMICE",
                run=lambda: R_STR_NHANES2,
                r_expected=R_STR_NHANES2,
                exact=True,
                narrative_after=N4_AFTER_STR,
            ),
            TutorialPart(
                r_code="imp <- mice(nhanes2, print=F)\nimp$meth",
                python_code="print(format_meth_r(names2, imp2.method))",
                run=lambda: format_meth_r(names2, imp2.method),
                r_expected=g("02", 4, 12),
                exact=True,
                narrative_after=N4_AFTER_METH2,
            ),
            TutorialPart(
                narrative_before=N4_BEFORE_METHODS,
                r_code="methods(mice)",
                python_code="# static R methods() listing (reference)",
                run=lambda: R_METHODS_MICE,
                r_expected=R_METHODS_MICE,
                exact=True,
                narrative_after=N4_AFTER_METHODS,
            ),
            TutorialPart(
                r_code="ini <- mice(nhanes2, maxit = 0)\nmeth <- ini$meth\nmeth",
                python_code=("meth = ini2.method.copy()\nprint(format_meth_r(names2, meth))"),
                run=lambda: format_meth_r(names2, dict(imp2.method)),
                r_expected=g("02", 4, 14),
                exact=True,
            ),
            TutorialPart(
                r_code='meth["bmi"] <- "norm"\nmeth',
                python_code='meth["bmi"] = "norm"\nprint(format_meth_r(names2, meth))',
                run=lambda: format_meth_r(names2, meth),
                r_expected=g("02", 4, 15),
                exact=True,
                narrative_after=N4_AFTER_NORM,
            ),
            TutorialPart(
                r_code="imp <- mice(nhanes2, meth = meth, print=F)",
                r_expected=R_MICE_METH,
                python_code="imp3 = mice(data2, column_names=names2, variable_specs=NHANES2_SPECS, method=meth, m=5, maxit=5, seed=123, print_flag=False)",
                run=lambda: "(custom methods imputation — no printed output)",
                partial=True,
                partial_reason="R vignette shows code only before trace plot.",
            ),
            TutorialPart(
                narrative_before=N4_BEFORE_PLOT,
                r_code="plot(imp)",
                python_code="plot_mids(imp3, variables=['bmi', 'hyp', 'chl'])",
                is_plot=True,
            ),
        ],
        images=[trace_nhanes2],
    )

    b.numbered_section(
        5,
        load_step_title(5),
        [
            TutorialPart(
                narrative_before=N5_BEFORE,
                r_code="imp40 <- mice.mids(imp, maxit=35, print=F)\nplot(imp40)",
                r_expected=R_MICE_SEED,
                python_code="plot_mids(imp40, variables=['bmi', 'hyp', 'chl'])",
                is_plot=True,
                plot_note="40-iteration trace via `continue_imputation(imp3, maxit=35)`.",
            ),
        ],
        images=[trace_40],
    )

    b.numbered_section(
        6,
        load_step_title(6),
        [
            TutorialPart(
                narrative_before=N6_BEFORE,
                r_code="stripplot(imp, chl~.imp, pch=20, cex=2)",
                python_code=(
                    "fig = plot_stripplot(imp3, 'chl')\n"
                    "save_figure(fig, ASSETS, 'v02_stripplot.png')"
                ),
                is_plot=True,
                narrative_after=N6_AFTER_STRIP,
            ),
            TutorialPart(
                narrative_before=N6_BEFORE_STRIP2,
                r_code="stripplot(imp)",
                python_code="_stripplot_panel(imp3, ['chl', 'bmi'])",
                is_plot=True,
                narrative_after=N6_AFTER_STRIP2,
            ),
        ],
        images=[strip_chl, strip_multi],
    )

    # --- Part: Repeated analysis in mice (steps 7–8) ---
    b.part("Repeated analysis in mice")

    b.numbered_section(
        7,
        load_step_title(7),
        [
            TutorialPart(
                narrative_before=N7_FORMULA,
                r_code="fit <- with(imp, lm(bmi ~ chl))\nfit",
                r_expected=g("02", 7, 21),
                python_code="print(format_mira_print_r(fit, nmis=imp3.nmis))",
                run=lambda: format_mira_print_r(fit, nmis=imp3.nmis),
                exact=True,
                narrative_after=N7_AFTER_FIT,
            ),
            TutorialPart(
                r_code="class(fit)",
                python_code='print(\'[1] "mira"   "matrix"\')',
                run=lambda: g("02", 7, 22),
                r_expected=g("02", 7, 22),
                exact=True,
            ),
            TutorialPart(
                narrative_before=N7_BEFORE_LS,
                r_code="ls(fit)",
                python_code='print(\'[1] "analyses" "call"     "call1"    "nmis"\')',
                run=lambda: g("02", 7, 23),
                r_expected=g("02", 7, 23),
                exact=True,
                narrative_after=N7_BEFORE_A2,
            ),
            TutorialPart(
                r_code="summary(fit$analyses[[2]])",
                python_code=(
                    "filled2 = complete(imp3, 2)\n"
                    "print(format_lm_summary_r('bmi ~ chl', filled2, names2))"
                ),
                run=lambda: format_lm_summary_r("bmi ~ chl", complete(imp3, 2), names2),
                r_expected=g("02", 7, 24),
                atol=0.15,
            ),
        ],
    )

    b.numbered_section(
        8,
        load_step_title(8),
        [
            TutorialPart(
                narrative_before=N8_BEFORE,
                r_code="pool.fit <- pool(fit)\nsummary(pool.fit)",
                python_code=("pooled = pool(fit)\nprint(format_pool_v02_r(summary_pool(pooled)))"),
                run=_pool_out,
                r_expected=g("02", 8, 25),
                atol=0.5,
                exact=True,
                narrative_after=N8_AFTER + "\n\n" + N8_AFTER_SCALAR,
            ),
        ],
    )

    return b.build()
