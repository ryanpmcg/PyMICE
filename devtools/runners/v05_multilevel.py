"""Vignette 05: Multilevel data — mirrors R tutorial (steps 1–26)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
from lib.compliance import VignetteBuilder
from lib.data import (
    load_popncr,
    load_popncr2,
    load_popncr3,
    load_popular,
    load_popular_truth,
    popncr_variable_specs,
)
from lib.golden import golden_output as g
from lib.parity_docs import GLOBAL_DISCLAIMER, V05_PARITY_OVERVIEW
from lib.r_style import (
    format_bool_vector_r,
    format_dataframe_r,
    format_icc_table_r,
    format_logged_events_warning_r,
    format_md_pattern_r,
    format_meth_r,
    format_mice_iter_log,
    format_popncr_head_r,
    format_predictor_matrix,
    format_summary_popncr_r,
    icc_aov,
)
from lib.report import VignetteReport
from lib.tutorial_section import TutorialPart
from lib.v05_narrative import (
    AUTHORS,
    N1_AFTER,
    N2_AFTER,
    N3_AFTER,
    N4_AFTER_HIST,
    N4_BEFORE_IND,
    N5_AFTER,
    N6_AFTER,
    N7_AFTER,
    N9_AFTER,
    N12_AFTER,
    N14_AFTER,
    N15_AFTER,
    N15_BEFORE,
    N16_AFTER,
    N18_AFTER,
    N19_DEFER,
    N20_AFTER,
    N21_2L_NORM,
    N22_AFTER,
    N23_AFTER,
    N25_EVAL,
    N26_CONCLUSION,
    N26_PMM,
    N26_REFERENCES,
    PART_CONVERGENCE,
    PART_INSPECTION,
    SERIES_LABEL,
    load_intro,
    load_step_title,
)
from lib.vignette_catalog import get_meta
from lib.vignette_rng import (
    ensure_vignette_r_prerequisites,
    run_v05_multilevel_chain,
)
from lib.viz import save_figure

from pymice import complete, md_pattern
from pymice.diagnostics.plots import (
    plot_density,
    plot_density_by_imp,
    plot_density_grid,
    plot_density_kde_lines,
    plot_histogram,
    plot_md_pattern,
    plot_mids,
)

_POP_DENSITY_XLIM = (-1.5, 10.0)
_POP_DENSITY_YLIM = (0.0, 0.35)

R_SETUP = ""
R_IMP1 = ""

ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"

ICC_VARS = ("popular", "popteach", "texp")


def _icc_values(
    data: np.ndarray, names: list[str], completed: np.ndarray | None = None
) -> list[float]:
    cls = names.index("class")
    group = data[:, cls]
    out: list[float] = []
    for var in ICC_VARS:
        yi = names.index(var)
        y = completed[:, yi] if completed is not None else data[:, yi]
        out.append(icc_aov(y, group))
    return out


def _popular_2l_pred(ini, names: list[str], *, pan: bool = False) -> np.ndarray:
    pred = ini.predictor_matrix.copy()
    pop_i = names.index("popular")
    if pan:
        pred[pop_i, :] = [0, -2, 2, 2, 1, 0, 2]
    else:
        pred[pop_i, :] = [0, -2, 2, 2, 2, 0, 2]
    return pred


def _popncr3_setup(ini, names: list[str]) -> tuple[dict[str, str], np.ndarray]:
    pred = ini.predictor_matrix.copy()
    pred[names.index("extrav"), :] = [0, -2, 0, 2, 2, 2, 2]
    pred[names.index("sex"), :] = [0, 1, 1, 0, 1, 1, 1]
    pred[names.index("texp"), :] = [0, -2, 1, 1, 0, 1, 1]
    pred[names.index("popular"), :] = [0, -2, 2, 2, 1, 0, 2]
    pred[names.index("popteach"), :] = [0, -2, 2, 2, 1, 2, 0]
    meth = dict(ini.method)
    meth.update(
        {
            "extrav": "2l.norm",
            "sex": "logreg",
            "texp": "2lonly.mean",
            "popular": "2l.pan",
            "popteach": "2l.pan",
        }
    )
    return meth, pred


def _norm_setup(ini, names: list[str]) -> tuple[dict[str, str], np.ndarray, np.ndarray]:
    meth = dict(ini.method)
    for var in ("extrav", "texp", "popular", "popteach"):
        meth[var] = "norm"
    pred = ini.predictor_matrix.copy()
    pred_no_class = pred.copy()
    pred_no_class[:, names.index("class")] = 0
    pred_no_class[:, names.index("pupil")] = 0
    pred_class = pred.copy()
    pred_class[:, names.index("pupil")] = 0
    return meth, pred_no_class, pred_class


def run() -> VignetteReport:
    ensure_vignette_r_prerequisites()
    data, names = load_popncr()
    pop_i = names.index("popular")
    pt_i = names.index("popteach")
    pop_miss = np.isnan(data[:, pop_i])

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
    ini = chain["ini"]
    meth = chain["meth"]
    pred_no_class = chain["pred_no_class"]
    chain["pred_class"]
    imp1 = chain["imp1"]
    imp2 = chain["imp2"]
    imp3 = chain["imp3"]
    imp3b = chain["imp3b"]
    imp4 = chain["imp4"]
    imp5 = chain["imp5"]
    imp5_15 = chain["imp5_15"]
    pred5 = chain["pred5"]
    imp6 = chain["imp6"]
    imp6_15 = chain["imp6_15"]
    pred6 = chain["pred6"]
    meth7 = chain["meth7"]
    pred7 = chain["pred7"]
    imp7 = chain["imp7"]
    imp8 = chain["imp8"]
    chain["ini3"]

    mp = md_pattern(data, names)
    texp_i = names.index("texp")
    no_texp_idx = [i for i in range(len(names)) if i != texp_i]
    mp_no_texp = md_pattern(data[:, no_texp_idx], [names[i] for i in no_texp_idx])

    popular_data, popular_names = load_popular()
    obs_icc = _icc_values(data, names)
    orig_icc = _icc_values(popular_data, popular_names)
    imp1_icc = _icc_values(data, names, complete(imp1, 1))
    imp2_icc = _icc_values(data, names, complete(imp2, 1))
    imp4_icc = _icc_values(data, names, complete(imp4, 1))

    ASSETS.mkdir(parents=True, exist_ok=True)
    md_pattern_img = save_figure(
        plot_md_pattern(mp),
        ASSETS,
        "v05_md_pattern.png",
    )
    md_pattern_no_texp_img = save_figure(
        plot_md_pattern(mp_no_texp),
        ASSETS,
        "v05_md_pattern_no_texp.png",
    )
    hist_pop = save_figure(
        plot_histogram(data, names, "popteach", condition=pop_miss),
        ASSETS,
        "v05_hist_popteach_by_popmiss.png",
    )
    hist_sex = save_figure(
        plot_histogram(data, names, "popteach", condition=np.isnan(data[:, names.index("sex")])),
        ASSETS,
        "v05_hist_popteach_by_sexmiss.png",
    )
    hist_extrav = save_figure(
        plot_histogram(data, names, "popteach", condition=np.isnan(data[:, names.index("extrav")])),
        ASSETS,
        "v05_hist_popteach_by_extravmiss.png",
    )
    hist_texp = save_figure(
        plot_histogram(data, names, "popteach", condition=np.isnan(data[:, texp_i])),
        ASSETS,
        "v05_hist_popteach_by_texpmiss.png",
    )
    hist_pop_by_pt = save_figure(
        plot_histogram(data, names, "popular", condition=np.isnan(data[:, pt_i])),
        ASSETS,
        "v05_hist_popular_by_ptmiss.png",
    )
    trace_imp2 = save_figure(
        plot_mids(imp2, variables=["popular", "texp", "popteach"]),
        ASSETS,
        "v05_trace_imp2.png",
    )
    trace_imp15 = save_figure(
        plot_mids(imp3, variables=["popular", "texp", "popteach"]),
        ASSETS,
        "v05_trace_imp15.png",
    )
    trace_imp35 = save_figure(
        plot_mids(imp3b, variables=["popular", "texp", "popteach"]),
        ASSETS,
        "v05_trace_imp35.png",
    )
    density_imp2_grid = save_figure(plot_density_grid(imp2), ASSETS, "v05_density_imp2_grid.png")
    density_imp2 = save_figure(plot_density(imp2, "popular"), ASSETS, "v05_density_imp2.png")
    density_imp2_by = save_figure(
        plot_density_by_imp(imp2, "popular"),
        ASSETS,
        "v05_density_imp2_by_imp.png",
    )
    density_imp4 = save_figure(plot_density_grid(imp4), ASSETS, "v05_density_imp4.png")
    density_imp4_pop = save_figure(
        plot_density(
            imp4,
            "popular",
            xlim=_POP_DENSITY_XLIM,
            ylim=_POP_DENSITY_YLIM,
        ),
        ASSETS,
        "v05_density_imp4_popular.png",
    )

    popular_truth = load_popular_truth()
    pop2_i = names2.index("popular")

    density_imp5 = save_figure(
        plot_density(
            imp5,
            "popular",
            xlim=_POP_DENSITY_XLIM,
            ylim=_POP_DENSITY_YLIM,
        ),
        ASSETS,
        "v05_density_imp5.png",
    )
    trace_imp5 = save_figure(plot_mids(imp5, variables=["popular"]), ASSETS, "v05_trace_imp5.png")
    trace_imp5_ext = save_figure(
        plot_mids(imp5_15, variables=["popular"]),
        ASSETS,
        "v05_trace_imp5_ext.png",
    )
    overlay_imp5 = save_figure(
        plot_density_kde_lines(
            {
                "truth": popular_truth,
                "2l.norm": complete(imp5, 1)[:, pop2_i],
                "PMM": complete(imp4, 1)[:, pop_i],
            },
            xlab="popular",
            colors={"truth": "black", "2l.norm": "red", "PMM": "green"},
        ),
        ASSETS,
        "v05_overlay_imp5_truth.png",
    )
    density_imp6 = save_figure(
        plot_density(
            imp6,
            "popular",
            xlim=_POP_DENSITY_XLIM,
            ylim=_POP_DENSITY_YLIM,
        ),
        ASSETS,
        "v05_density_imp6.png",
    )
    trace_imp6 = save_figure(plot_mids(imp6, variables=["popular"]), ASSETS, "v05_trace_imp6.png")
    trace_imp6_ext = save_figure(
        plot_mids(imp6_15, variables=["popular"]),
        ASSETS,
        "v05_trace_imp6_ext.png",
    )
    overlay_imp6 = save_figure(
        plot_density_kde_lines(
            {
                "truth": popular_truth,
                "2l.pan": complete(imp6, 1)[:, pop2_i],
                "PMM": complete(imp4, 1)[:, pop_i],
            },
            xlab="popular",
            title="black = truth | green = PMM | red = 2l.pan",
            colors={"truth": "black", "2l.pan": "red", "PMM": "green"},
        ),
        ASSETS,
        "v05_overlay_imp6_truth.png",
    )
    density_imp7 = save_figure(plot_density_grid(imp7), ASSETS, "v05_density_imp7.png")
    trace_imp7_a = save_figure(
        plot_mids(imp7, variables=["extrav", "sex", "texp"]),
        ASSETS,
        "v05_trace_imp7_a.png",
    )
    trace_imp7_b = save_figure(
        plot_mids(imp7, variables=["popular", "popteach"]),
        ASSETS,
        "v05_trace_imp7_b.png",
    )
    density_imp8 = save_figure(plot_density_grid(imp8), ASSETS, "v05_density_imp8.png")
    trace_imp8_a = save_figure(
        plot_mids(imp8, variables=["extrav", "sex", "texp"]),
        ASSETS,
        "v05_trace_imp8_a.png",
    )
    trace_imp8_b = save_figure(
        plot_mids(imp8, variables=["popular", "popteach"]),
        ASSETS,
        "v05_trace_imp8_b.png",
    )

    b = VignetteBuilder.from_meta(get_meta("05"))
    b.set_intro(load_intro(), authors=AUTHORS, series_label=SERIES_LABEL)
    b.set_disclaimer(GLOBAL_DISCLAIMER)
    b.set_parity_overview(V05_PARITY_OVERVIEW)

    b.numbered_section(
        1,
        load_step_title(1),
        [
            TutorialPart(
                r_code="require(mice)\nrequire(lattice)\nrequire(pan)\nset.seed(123)",
                r_expected=R_SETUP,
                python_code=(
                    "import numpy as np\n"
                    "from pymice import mice, complete, md_pattern, pool, summary_pool, with_mids\n"
                    "from pymice.diagnostics.plots import plot_histogram, plot_mids, plot_density\n"
                    "from lib.data import load_popncr\n"
                    "from lib.viz import save_figure\n"
                    "from lib.r_style import (\n"
                    "    format_dataframe_r,\n"
                    "    format_summary_popncr_r,\n"
                    "    format_md_pattern_r,\n"
                    "    format_bool_vector_r,\n"
                    "    format_predictor_matrix,\n"
                    "    format_pool_tibble_r\n"
                    ")"
                ),
                run=lambda: "(setup — no console output)",
                partial=True,
                partial_reason="Package load step; workspace `ls()` not reproduced.",
                narrative_after=N1_AFTER,
            ),
        ],
    )

    b.part(PART_INSPECTION)

    b.numbered_section(
        2,
        load_step_title(2),
        [
            TutorialPart(
                r_code="head(popNCR)",
                python_code="print(format_dataframe_r(data[:6], names))",
                run=lambda: format_dataframe_r(data[:6], names),
                r_expected=g("05", 2, 3),
                exact=True,
            ),
            TutorialPart(
                r_code="dim(popNCR)",
                python_code='print(f"[1] {data.shape[0]}    {data.shape[1]}")',
                run=lambda: f"[1] {data.shape[0]}    {data.shape[1]}",
                r_expected="[1] 2000    7",
                exact=True,
            ),
            TutorialPart(
                r_code="nrow(popNCR)",
                python_code="print(f'[1] {data.shape[0]}')",
                run=lambda: f"[1] {data.shape[0]}",
                r_expected="[1] 2000",
                exact=True,
            ),
            TutorialPart(
                r_code="ncol(popNCR)",
                python_code="print(f'[1] {data.shape[1]}')",
                run=lambda: f"[1] {data.shape[1]}",
                r_expected="[1] 7",
                exact=True,
            ),
            TutorialPart(
                r_code="summary(popNCR)",
                r_expected=g("05", 2, 7),
                python_code="print(format_summary_popncr_r(data, names))",
                run=lambda: format_summary_popncr_r(data, names),
                exact=True,
                narrative_after=N2_AFTER,
            ),
        ],
    )

    b.numbered_section(
        3,
        load_step_title(3),
        [
            TutorialPart(
                r_code="md.pattern(popNCR)",
                python_code="print(format_md_pattern_r(mp))",
                run=lambda: format_md_pattern_r(mp),
                r_expected=g("05", 3, 8),
                exact=True,
            ),
            TutorialPart(
                r_code="md.pattern(popNCR[ , -5])",
                python_code="print(format_md_pattern_r(mp_no_texp))",
                run=lambda: format_md_pattern_r(mp_no_texp),
                r_expected=g("05", 3, 9),
                exact=True,
                narrative_after=N3_AFTER,
            ),
        ],
        images=[md_pattern_img, md_pattern_no_texp_img],
    )

    b.numbered_section(
        4,
        load_step_title(4),
        [
            TutorialPart(
                narrative_before=N4_BEFORE_IND,
                r_code="is.na(popNCR$popular)",
                r_expected=g("05", 4, 10),
                python_code="print(format_bool_vector_r(pop_miss, max_lines=None, width=12))",
                run=lambda: format_bool_vector_r(pop_miss, max_lines=None, width=12),
                exact=True,
            ),
            TutorialPart(
                r_code="histogram(~ popteach | is.na(popular), data=popNCR)",
                python_code="plot_histogram(data, names, 'popteach', condition=pop_miss)",
                is_plot=True,
                narrative_after=N4_AFTER_HIST,
            ),
        ],
        images=[hist_pop],
    )

    b.numbered_section(
        5,
        load_step_title(5),
        [
            TutorialPart(
                r_code="histogram(~ popteach | is.na(sex), data = popNCR)",
                python_code=(
                    "plot_histogram(data, names, 'popteach', "
                    "condition=np.isnan(data[:, names.index('sex')]))"
                ),
                is_plot=True,
            ),
            TutorialPart(
                r_code="histogram(~ popteach | is.na(extrav), data = popNCR)",
                python_code=(
                    "plot_histogram(data, names, 'popteach', "
                    "condition=np.isnan(data[:, names.index('extrav')]))"
                ),
                is_plot=True,
            ),
            TutorialPart(
                r_code="histogram(~ popteach | is.na(texp), data = popNCR)",
                python_code="plot_histogram(data, names, 'popteach', condition=np.isnan(data[:, texp_i]))",
                is_plot=True,
                narrative_after=N5_AFTER,
            ),
        ],
        images=[hist_sex, hist_extrav, hist_texp],
    )

    b.numbered_section(
        6,
        load_step_title(6),
        [
            TutorialPart(
                r_code="histogram(~ popular | is.na(popteach), data = popNCR)",
                python_code=(
                    "plot_histogram(data, names, 'popular', "
                    "condition=np.isnan(data[:, names.index('popteach')]))"
                ),
                is_plot=True,
                narrative_after=N6_AFTER,
            ),
        ],
        images=[hist_pop_by_pt],
    )

    b.numbered_section(
        7,
        load_step_title(7),
        [
            TutorialPart(
                r_code="icc(aov(popular ~ as.factor(class), data = popNCR))",
                python_code="print(f'[1] {obs_icc[0]:.7f}')",
                run=lambda: f"[1] {obs_icc[0]:.7f}",
                r_expected=g("05", 7, 16),
                atol=1e-5,
            ),
            TutorialPart(
                r_code="icc(aov(popteach ~ class, data = popNCR))",
                python_code="print(f'[1] {obs_icc[1]:.7f}')",
                run=lambda: f"[1] {obs_icc[1]:.7f}",
                r_expected=g("05", 7, 17),
                atol=1e-5,
            ),
            TutorialPart(
                r_code="icc(aov(texp ~ class, data = popNCR))",
                python_code="print(f'[1] {obs_icc[2]:.7f}')",
                run=lambda: f"[1] {obs_icc[2]:.7f}",
                r_expected=g("05", 7, 18),
                atol=1e-5,
                narrative_after=N7_AFTER,
            ),
        ],
    )

    b.numbered_section(
        8,
        load_step_title(8),
        [
            TutorialPart(
                r_code="ini <- mice(popNCR, maxit = 0)\nmeth <- ini$meth\nmeth",
                python_code=(
                    "ini = mice(data, column_names=names, maxit=0, print_flag=False)\n"
                    "print(format_meth_r(names, ini.method, style='popncr'))"
                ),
                run=lambda: format_meth_r(names, ini.method, style="popncr"),
                r_expected=g("05", 8, 19),
                exact=True,
            ),
            TutorialPart(
                r_code='meth[c(3, 5, 6, 7)] <- "norm"\nmeth',
                python_code=(
                    "meth = dict(ini.method)\n"
                    'for v in ("extrav", "texp", "popular", "popteach"):\n'
                    '    meth[v] = "norm"\n'
                    "print(format_meth_r(names, meth, style='popncr'))"
                ),
                run=lambda: format_meth_r(names, meth, style="popncr"),
                r_expected=g("05", 8, 20),
                exact=True,
            ),
            TutorialPart(
                r_code="pred <- ini$pred\npred",
                python_code=(
                    "print(format_predictor_matrix(names, ini.predictor_matrix, style='popncr'))"
                ),
                run=lambda: format_predictor_matrix(names, ini.predictor_matrix, style="popncr"),
                r_expected=g("05", 8, 21),
                exact=True,
            ),
            TutorialPart(
                r_code='pred[, "class"] <- 0\npred[, "pupil"] <- 0\npred',
                python_code=(
                    "pred_nc = pred_no_class.copy()\n"
                    "print(format_predictor_matrix(names, pred_nc, style='popncr'))"
                ),
                run=lambda: format_predictor_matrix(names, pred_no_class, style="popncr"),
                r_expected=g("05", 8, 22),
                exact=True,
            ),
            TutorialPart(
                r_code="imp1 <- mice(popNCR, meth = meth, pred = pred, print = FALSE)",
                r_expected=R_IMP1,
                python_code=(
                    "imp1 = mice(data, column_names=names, method=meth, "
                    "predictor_matrix=pred_no_class, m=5, maxit=5, print_flag=False)"
                ),
                run=lambda: "(imp1 created — no console output)",
                partial=True,
                partial_reason="Creates `imp1` mids object.",
            ),
        ],
    )

    b.numbered_section(
        9,
        load_step_title(9),
        [
            TutorialPart(
                r_code="summary(complete(imp1))",
                r_expected=g("05", 9, 24),
                python_code="print(format_summary_popncr_r(complete(imp1, 1), names, imputed=True))",
                run=lambda: format_summary_popncr_r(complete(imp1, 1), names, imputed=True),
                partial=True,
                partial_reason="Imputed norm summaries within atol=0.2 (session chain; sex counts may differ by 1).",
                atol=0.2,
            ),
            TutorialPart(
                r_code="summary(popNCR)",
                r_expected=g("05", 9, 25),
                python_code="print(format_summary_popncr_r(data, names))",
                run=lambda: format_summary_popncr_r(data, names),
                exact=True,
                narrative_after=N9_AFTER,
            ),
        ],
    )

    b.numbered_section(
        10,
        load_step_title(10),
        [
            TutorialPart(
                r_code=(
                    "data.frame(vars = names(popNCR[c(6, 7, 5)]),\n"
                    "           observed = c(icc(aov(popular ~ class, popNCR)),\n"
                    "                        icc(aov(popteach ~ class, popNCR)),\n"
                    "                        icc(aov(texp ~ class, popNCR))),\n"
                    "           norm     = c(icc(aov(popular ~ class, complete(imp1))),\n"
                    "                        icc(aov(popteach ~ class, complete(imp1))),\n"
                    "                        icc(aov(texp ~ class, complete(imp1)))))"
                ),
                python_code=(
                    "print(format_icc_table_r(list(ICC_VARS), "
                    "{'observed': obs_icc, 'norm': imp1_icc}))"
                ),
                run=lambda: format_icc_table_r(
                    list(ICC_VARS), {"observed": obs_icc, "norm": imp1_icc}
                ),
                r_expected=g("05", 10, 26),
                atol=5e-4,
            ),
        ],
    )

    b.numbered_section(
        11,
        load_step_title(11),
        [
            TutorialPart(
                r_code=(
                    'pred <- ini$pred\npred[, "pupil"] <- 0\n'
                    "imp2 <- mice(popNCR, meth = meth, pred = pred, print = FALSE)"
                ),
                python_code=(
                    "pred = ini.predictor_matrix.copy()\n"
                    "pred[:, names.index('pupil')] = 0\n"
                    "imp2 = mice(data, column_names=names, method=meth, "
                    "predictor_matrix=pred, m=5, maxit=5, print_flag=False)\n"
                    "print(format_logged_events_warning_r(len(imp2.logged_events)))"
                ),
                run=lambda: format_logged_events_warning_r(len(imp2.logged_events)),
                r_expected=g("05", 11, 27),
                exact=True,
            ),
        ],
    )

    b.numbered_section(
        12,
        load_step_title(12),
        [
            TutorialPart(
                r_code=(
                    "data.frame(vars = names(popNCR[c(6, 7, 5)]),\n"
                    "           observed  = c(icc(aov(popular ~ class, popNCR)),\n"
                    "                         icc(aov(popteach ~ class, popNCR)),\n"
                    "                         icc(aov(texp ~ class, popNCR))),\n"
                    "           norm      = c(icc(aov(popular ~ class, complete(imp1))),\n"
                    "                         icc(aov(popteach ~ class, complete(imp1))),\n"
                    "                         icc(aov(texp ~ class, complete(imp1)))),\n"
                    "           normclass = c(icc(aov(popular ~ class, complete(imp2))),\n"
                    "                         icc(aov(popteach ~ class, complete(imp2))),\n"
                    "                         icc(aov(texp ~ class, complete(imp2)))))"
                ),
                python_code=(
                    "print(format_icc_table_r(list(ICC_VARS), "
                    "{'observed': obs_icc, 'norm': imp1_icc, 'normclass': imp2_icc}))"
                ),
                run=lambda: format_icc_table_r(
                    list(ICC_VARS),
                    {"observed": obs_icc, "norm": imp1_icc, "normclass": imp2_icc},
                ),
                r_expected=g("05", 12, 28),
                atol=0.05,
                narrative_after=N12_AFTER,
            ),
        ],
    )

    b.part(PART_CONVERGENCE)

    b.numbered_section(
        13,
        load_step_title(13),
        [
            TutorialPart(
                r_code='plot(imp2, c("popular", "texp", "popteach"))',
                python_code="plot_mids(imp2, variables=['popular', 'texp', 'popteach'])",
                is_plot=True,
            ),
        ],
        images=[trace_imp2],
    )

    b.numbered_section(
        14,
        load_step_title(14),
        [
            TutorialPart(
                r_code="imp3 <- mice.mids(imp2, maxit = 10)\nplot(imp3, c(...))",
                python_code=(
                    "imp3 = continue_imputation(imp2, maxit=10, print=False)\n"
                    "plot_mids(imp3, variables=['popular', 'texp', 'popteach'])"
                ),
                is_plot=True,
                plot_note="Warm-started via `continue_imputation` (R `mice.mids`).",
            ),
            TutorialPart(
                r_code=(
                    "imp3b <- mice.mids(imp3, maxit = 20, print = FALSE)\n"
                    'plot(imp3b, c("popular", "texp", "popteach"))'
                ),
                python_code=(
                    "imp3b = continue_imputation(imp3, maxit=20, print=False)\n"
                    "plot_mids(imp3b, variables=['popular', 'texp', 'popteach'])"
                ),
                is_plot=True,
                plot_note="Second `continue_imputation` extension (35 iterations total).",
                narrative_after=N14_AFTER,
            ),
        ],
        images=[trace_imp15, trace_imp35],
    )

    b.numbered_section(
        15,
        load_step_title(15),
        [
            TutorialPart(
                narrative_before=N15_BEFORE,
                r_code="densityplot(imp2)",
                python_code="plot_density_grid(imp2)",
                is_plot=True,
            ),
            TutorialPart(
                r_code="densityplot(imp2, ~ popular)",
                python_code="plot_density(imp2, 'popular')",
                is_plot=True,
            ),
            TutorialPart(
                r_code="densityplot(imp2, ~ popular | .imp)",
                python_code="plot_density_by_imp(imp2, 'popular')",
                is_plot=True,
                narrative_after=N15_AFTER,
            ),
        ],
        images=[density_imp2_grid, density_imp2, density_imp2_by],
    )

    b.numbered_section(
        16,
        load_step_title(16),
        [
            TutorialPart(
                r_code="head(complete(imp2, 1), n = 15)",
                r_expected=g("05", 16, 37),
                python_code="print(format_popncr_head_r(complete(imp2, 1), names, n=15))",
                run=lambda: format_popncr_head_r(complete(imp2, 1), names, n=15),
                exact=True,
                narrative_after=N16_AFTER,
            ),
        ],
    )

    b.numbered_section(
        17,
        load_step_title(17),
        [
            TutorialPart(
                r_code="imp4 <- mice(popNCR)",
                r_expected=g("05", 17, 38),
                python_code=(
                    "imp4 = mice(data, column_names=names, m=5, maxit=5, print_flag=False)\n"
                    "print(format_mice_iter_log(\n"
                    "    imp4.m, imp4.iteration, imp4.visit_sequence,\n"
                    "    imputed_vars=['extrav', 'sex', 'texp', 'popular', 'popteach'],\n"
                    "    warning=format_logged_events_warning_r(len(imp4.logged_events)),\n"
                    "))"
                ),
                run=lambda: format_mice_iter_log(
                    imp4.m,
                    imp4.iteration,
                    imp4.visit_sequence,
                    imputed_vars=["extrav", "sex", "texp", "popular", "popteach"],
                    warning=format_logged_events_warning_r(len(imp4.logged_events)),
                ),
                exact=True,
            ),
        ],
    )

    b.numbered_section(
        18,
        load_step_title(18),
        [
            TutorialPart(
                r_code="densityplot(imp4)",
                r_expected="",
                python_code="plot_density_grid(imp4)",
                is_plot=True,
                narrative_after=N18_AFTER,
            ),
        ],
        images=[density_imp4],
    )

    b.numbered_section(
        19,
        load_step_title(19),
        [
            TutorialPart(
                r_code="# See exercise 20 for ICC comparison with imp4",
                r_expected="",
                python_code="# ICC table deferred to step 20",
                skip=True,
                skip_reason="R vignette refers to exercise 20 for the full ICC table.",
                narrative_before=N19_DEFER,
            ),
        ],
    )

    b.numbered_section(
        20,
        load_step_title(20),
        [
            TutorialPart(
                r_code=(
                    "data.frame(vars      = names(popNCR[c(6, 7, 5)]),\n"
                    "           observed  = c(icc(aov(popular ~ class, popNCR)),\n"
                    "                         icc(aov(popteach ~ class, popNCR)),\n"
                    "                         icc(aov(texp ~ class, popNCR))),\n"
                    "           norm      = c(icc(aov(popular ~ class, complete(imp1))),\n"
                    "                         icc(aov(popteach ~ class, complete(imp1))),\n"
                    "                         icc(aov(texp ~ class, complete(imp1)))),\n"
                    "           normclass = c(icc(aov(popular ~ class, complete(imp2))),\n"
                    "                         icc(aov(popteach ~ class, complete(imp2))),\n"
                    "                         icc(aov(texp ~ class, complete(imp2)))),\n"
                    "           pmm       = c(icc(aov(popular ~ class, complete(imp4))),\n"
                    "                         icc(aov(popteach ~ class, complete(imp4))),\n"
                    "                         icc(aov(texp ~ class, complete(imp4)))),\n"
                    "           orig      = c(icc(aov(popular ~ as.factor(class), popular)),\n"
                    "                         icc(aov(popteach ~ as.factor(class), popular)),\n"
                    "                         icc(aov(texp ~ as.factor(class), popular))))"
                ),
                python_code=(
                    "print(format_icc_table_r(list(ICC_VARS), "
                    "{'observed': obs_icc, 'norm': imp1_icc, 'normclass': imp2_icc, "
                    "'pmm': imp4_icc, 'orig': orig_icc}))"
                ),
                run=lambda: format_icc_table_r(
                    list(ICC_VARS),
                    {
                        "observed": obs_icc,
                        "norm": imp1_icc,
                        "normclass": imp2_icc,
                        "pmm": imp4_icc,
                        "orig": orig_icc,
                    },
                ),
                r_expected=g("05", 20, 40),
                atol=0.05,
                narrative_after=N20_AFTER,
            ),
        ],
    )

    b.numbered_section(
        21,
        load_step_title(21),
        [
            TutorialPart(
                r_code=(
                    "ini <- mice(popNCR2, maxit = 0)\npred <- ini$pred\n"
                    'pred["popular", ] <- c(0, -2, 2, 2, 2, 0, 2)\n'
                    'meth <- c("", "", "", "", "", "2l.norm", "")\n'
                    "imp5 <- mice(popNCR2, pred = pred, meth=meth, print = FALSE)"
                ),
                r_expected="",
                python_code=(
                    "ini2 = mice(data2, column_names=names2, maxit=0)\n"
                    "pred5 = ini2.predictor_matrix.copy()\n"
                    "pred5[names2.index('popular'), :] = [0, -2, 2, 2, 2, 0, 2]\n"
                    "meth5 = dict(ini2.method); meth5['popular'] = '2l.norm'\n"
                    "imp5 = mice(data2, column_names=names2, method=meth5, "
                    "predictor_matrix=pred5, m=5, maxit=5)\n"
                    "print(format_predictor_matrix(names2, pred5, style='popncr'))"
                ),
                run=lambda: format_predictor_matrix(names2, pred5, style="popncr"),
                partial=True,
                partial_reason="`pred`/`meth` setup exact; `2l.norm` imputed values differ (sampler moment tolerance ~0.15).",
                narrative_after=N21_2L_NORM,
            ),
        ],
    )

    b.numbered_section(
        22,
        load_step_title(22),
        [
            TutorialPart(
                r_code="densityplot(imp5, ~popular, ylim = c(0, 0.35), xlim = c(-1.5, 10))",
                python_code=("plot_density(imp5, 'popular', xlim=(-1.5, 10.0), ylim=(0.0, 0.35))"),
                is_plot=True,
                plot_note="Matplotlib density panel; `2l.norm` curve within moment tolerance ~0.15 vs R.",
            ),
            TutorialPart(
                r_code="densityplot(imp4, ~popular, ylim = c(0, 0.35), xlim = c(-1.5, 10))",
                python_code=("plot_density(imp4, 'popular', xlim=(-1.5, 10.0), ylim=(0.0, 0.35))"),
                is_plot=True,
                plot_note="PMM reference density (session chain).",
            ),
            TutorialPart(
                r_code=(
                    "plot(density(popular$popular))  #true data\n"
                    'lines(density(complete(imp5)$popular), col = "red", lwd = 2)  #2l.norm\n'
                    'lines(density(complete(imp4)$popular), col = "green", lwd = 2)  #PMM'
                ),
                python_code=(
                    "plot_density_kde_lines(\n"
                    "    {'truth': popular_truth, '2l.norm': complete(imp5, 1)[:, pop2_i],\n"
                    "     'PMM': complete(imp4, 1)[:, pop_i]},\n"
                    "    xlab='popular',\n"
                    "    colors={'truth': 'black', '2l.norm': 'red', 'PMM': 'green'},\n"
                    ")"
                ),
                is_plot=True,
                plot_note="Truth density from `popular.csv`; `2l.norm` overlay within moment tolerance ~0.15.",
            ),
            TutorialPart(
                r_code="plot(imp5)",
                python_code="plot_mids(imp5, variables=['popular'])",
                is_plot=True,
                plot_note="Convergence trace; shape matches R, not pixel-identical.",
            ),
            TutorialPart(
                r_code="imp5.b <- mice.mids(imp5, maxit = 10, print = FALSE)\nplot(imp5.b)",
                python_code=(
                    "imp5_15 = continue_imputation(imp5, maxit=10, print=False)\n"
                    "plot_mids(imp5_15, variables=['popular'])"
                ),
                is_plot=True,
                plot_note="Extended trace via `continue_imputation(imp5, maxit=10)`.",
                narrative_after=N22_AFTER,
            ),
        ],
        images=[density_imp5, density_imp4_pop, overlay_imp5, trace_imp5, trace_imp5_ext],
    )

    b.numbered_section(
        23,
        load_step_title(23),
        [
            TutorialPart(
                r_code=(
                    "ini <- mice(popNCR2, maxit = 0)\n"
                    "pred <- ini$pred\n"
                    'pred["popular", ] <- c(0, -2, 2, 2, 1, 0, 2)\n'
                    "meth <- ini$meth\n"
                    'meth <- c("", "", "", "", "", "2l.pan", "")\n'
                    "imp6 <- mice(popNCR2, pred = pred, meth = meth, print = FALSE)"
                ),
                python_code=(
                    "pred6[names2.index('popular'), :] = [0, -2, 2, 2, 1, 0, 2]\n"
                    "meth6['popular'] = '2l.pan'\n"
                    "imp6 = mice(data2, column_names=names2, method=meth6, "
                    "predictor_matrix=pred6, m=5, maxit=5)"
                ),
                run=lambda: format_predictor_matrix(names2, pred6, style="popncr"),
                partial=True,
                partial_reason="`pred`/`meth` setup exact; `2l.pan` imputed values differ (sampler moment tolerance ~0.15).",
            ),
            TutorialPart(
                r_code="densityplot(imp6, ~popular, ylim = c(0, 0.35), xlim = c(-1.5, 10))",
                python_code=("plot_density(imp6, 'popular', xlim=(-1.5, 10.0), ylim=(0.0, 0.35))"),
                is_plot=True,
                plot_note="Matplotlib density panel; `2l.pan` curve within moment tolerance ~0.15 vs R.",
            ),
            TutorialPart(
                r_code="densityplot(imp4, ~popular, ylim = c(0, 0.35), xlim = c(-1.5, 10))",
                python_code=("plot_density(imp4, 'popular', xlim=(-1.5, 10.0), ylim=(0.0, 0.35))"),
                is_plot=True,
                plot_note="PMM reference density (session chain).",
            ),
            TutorialPart(
                r_code=(
                    'plot(density(popular$popular), main = "black = truth | green = PMM | red = 2l.pan")  #\n'
                    'lines(density(complete(imp6)$popular), col = "red", lwd = 2)  #2l.pan\n'
                    'lines(density(complete(imp4)$popular), col = "green", lwd = 2)  #PMM'
                ),
                python_code=(
                    "plot_density_kde_lines(\n"
                    "    {'truth': popular_truth, '2l.pan': complete(imp6, 1)[:, pop2_i],\n"
                    "     'PMM': complete(imp4, 1)[:, pop_i]},\n"
                    "    xlab='popular',\n"
                    "    title='black = truth | green = PMM | red = 2l.pan',\n"
                    "    colors={'truth': 'black', '2l.pan': 'red', 'PMM': 'green'},\n"
                    ")"
                ),
                is_plot=True,
                plot_note="Truth density; `2l.pan` overlay within moment tolerance ~0.15.",
            ),
            TutorialPart(
                r_code="plot(imp6)",
                python_code="plot_mids(imp6, variables=['popular'])",
                is_plot=True,
                plot_note="Convergence trace; shape matches R, not pixel-identical.",
            ),
            TutorialPart(
                r_code="imp6.b <- mice.mids(imp5, maxit = 10, print = FALSE)\nplot(imp6.b)",
                python_code=(
                    "imp6_15 = continue_imputation(imp6, maxit=10, print=False)\n"
                    "plot_mids(imp6_15, variables=['popular'])"
                ),
                is_plot=True,
                plot_note="R vignette extends imp5 by mistake; PyMICE correctly extends imp6.",
                narrative_after=N23_AFTER,
            ),
        ],
        images=[
            density_imp6,
            density_imp4_pop,
            overlay_imp6,
            trace_imp6,
            trace_imp6_ext,
        ],
    )

    b.numbered_section(
        24,
        load_step_title(24),
        [
            TutorialPart(
                r_code=(
                    "ini <- mice(popNCR3, maxit = 0)\n"
                    "pred <- ini$pred\n"
                    'pred["extrav", ] <- c(0, -2, 0, 2, 2, 2, 2)  #2l.norm\n'
                    'pred["sex", ] <- c(0, 1, 1, 0, 1, 1, 1)  #2logreg\n'
                    'pred["texp", ] <- c(0, -2, 1, 1, 0, 1, 1)  #2lonly.mean\n'
                    'pred["popular", ] <- c(0, -2, 2, 2, 1, 0, 2)  #2l.pan\n'
                    'pred["popteach", ] <- c(0, -2, 2, 2, 1, 2, 0)  #2l.pan\n'
                    "meth <- ini$meth\n"
                    'meth <- c("", "", "2l.norm", "logreg", "2lonly.mean", "2l.pan", "2l.pan")\n'
                    "imp7 <- mice(popNCR3, pred = pred, meth = meth, print = FALSE)"
                ),
                python_code=(
                    "meth7, pred7 = _popncr3_setup(ini3, names3)\n"
                    "imp7 = mice(data3, column_names=names3, method=meth7, "
                    "predictor_matrix=pred7, m=5, maxit=5)"
                ),
                run=lambda: (
                    format_meth_r(names3, meth7, style="popncr")
                    + "\n"
                    + format_predictor_matrix(names3, pred7, style="popncr")
                ),
                partial=True,
                partial_reason="`meth`/`pred` setup exact; multilevel imputations differ (sampler moment tolerance ~0.15).",
            ),
        ],
    )

    b.numbered_section(
        25,
        load_step_title(25),
        [
            TutorialPart(
                r_code="densityplot(imp7)",
                python_code="plot_density_grid(imp7)",
                is_plot=True,
                plot_note="Multilevel density grid; imputed marginals within moment tolerance ~0.15.",
            ),
            TutorialPart(
                r_code="plot(imp7)",
                python_code=(
                    "plot_mids(imp7, variables=['extrav','sex','texp'])\n"
                    "plot_mids(imp7, variables=['popular','popteach'])"
                ),
                is_plot=True,
                plot_note="Convergence traces for mixed `2l.norm`/`2l.pan`/`logreg`/`2lonly.mean` setup.",
                narrative_after=N25_EVAL,
            ),
        ],
        images=[density_imp7, trace_imp7_a, trace_imp7_b],
    )

    b.numbered_section(
        26,
        load_step_title(26),
        [
            TutorialPart(
                r_code=(
                    "pmmdata <- popNCR3\npmmdata$class <- as.factor(popNCR3$class)\n"
                    "imp8 <- mice(pmmdata, m = 5, print = FALSE)"
                ),
                python_code=(
                    "imp8 = mice(data3, column_names=names3, m=5, maxit=5, print_flag=False)\n"
                    "print(format_logged_events_warning_r(len(imp8.logged_events)))"
                ),
                run=lambda: format_logged_events_warning_r(len(imp8.logged_events)),
                r_expected=g("05", 26, 57),
                exact=True,
            ),
            TutorialPart(
                narrative_before=N26_PMM,
                r_code="densityplot(imp8)",
                python_code="plot_density_grid(imp8)",
                is_plot=True,
                plot_note="Default PMM on `popNCR3`; imputed marginals differ (draw-order on session chain).",
            ),
            TutorialPart(
                r_code="plot(imp8)",
                python_code=(
                    "plot_mids(imp8, variables=['extrav','sex','texp'])\n"
                    "plot_mids(imp8, variables=['popular','popteach'])"
                ),
                is_plot=True,
                plot_note="PMM convergence traces; matplotlib equivalent of R `plot(imp8)`.",
                narrative_after=N26_CONCLUSION + "\n\n" + N26_REFERENCES,
            ),
        ],
        images=[density_imp8, trace_imp8_a, trace_imp8_b],
    )

    return b.build()
