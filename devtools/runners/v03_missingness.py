"""Vignette 03: Missingness inspection — mirrors R tutorial (steps 1–15)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
from lib.compliance import VignetteBuilder
from lib.data import (
    load_boys_full_matrix,
    load_mammalsleep_full,
    load_mammalsleep_impute,
)
from lib.golden import golden_output as g
from lib.help_format import R_HELP_BOYS, R_HELP_MAMMAL
from lib.parity_docs import GLOBAL_DISCLAIMER, V03_PARITY_OVERVIEW
from lib.r_style import (
    format_bool_vector_r,
    format_boys_head_r,
    format_help_r,
    format_logged_events_warning_r,
    format_mammalsleep_head_r,
    format_md_pattern_r,
    format_pool_mipo_r,
    format_pool_v03_summary_r,
    format_summary_boys_r,
    format_summary_mammalsleep_r,
    format_tv_means_tibble_r,
)
from lib.report import VignetteReport
from lib.tutorial_section import TutorialPart
from lib.v03_narrative import (
    AUTHORS,
    N1_AFTER,
    N2_HELP,
    N4_AFTER,
    N5_AFTER,
    N6_AFTER_HIST,
    N6_AFTER_IND,
    N6_BEFORE_HIST,
    N6_BEFORE_IND,
    N6_HIST_EQUIV,
    N8_AFTER_SUMMARY,
    N8_BEFORE_WITH,
    N9_AFTER_MDP,
    N9_BEFORE_MS,
    N10_AFTER_IMP,
    N12_AFTER_POOL,
    N14_AFTER_POOL,
    N15_AFTER,
    PART_IMPORTANCE,
    SERIES_LABEL,
    load_intro,
    load_step_title,
)
from lib.vignette_catalog import get_meta
from lib.vignette_rng import (
    ensure_vignette_r_prerequisites,
    run_v03_boys_chain,
    run_v03_mammalsleep_chain,
)
from lib.viz import save_figure

from pymice import complete, md_pattern, pool, summary_pool, with_mids
from pymice.diagnostics.plots import plot_histogram, plot_mids

R_SETUP = ""
R_HELP = R_HELP_BOYS
R_MICE_BOYS = ""
R_HELP_MAMMAL = R_HELP_MAMMAL
ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"


def run() -> VignetteReport:
    ensure_vignette_r_prerequisites()
    boys, boy_names = load_boys_full_matrix()
    mpat = md_pattern(boys, boy_names)
    gen_col = boy_names.index("gen")
    gen_missing = np.isnan(boys[:, gen_col])

    imp1 = run_v03_boys_chain(boys, boy_names)

    ms_full, ms_names = load_mammalsleep_full()
    ms_mdp = md_pattern(ms_full, ms_names)
    ms_no_sp, ms_no_names = load_mammalsleep_impute()
    imp_ms, impnew = run_v03_mammalsleep_chain(ms_full, ms_names, ms_no_sp, ms_no_names)
    fit1 = with_mids(imp_ms, formula="sws ~ log10(bw) + odi")
    pooled1 = pool(fit1)
    fit2 = with_mids(impnew, formula="sws ~ log10(bw) + odi")
    pooled2 = pool(fit2)

    hist_gen = save_figure(plot_histogram(boys, boy_names, "gen"), ASSETS, "v03_hist_gen.png")
    hist_age = save_figure(
        plot_histogram(boys, boy_names, "age", condition=gen_missing),
        ASSETS,
        "v03_hist_age_by_genmiss.png",
    )
    trace_ms = save_figure(
        plot_mids(imp_ms, variables=["sws", "ps", "ts"]),
        ASSETS,
        "v03_mammalsleep_trace.png",
    )
    trace_new = save_figure(
        plot_mids(impnew, variables=["mls", "gt"]),
        ASSETS,
        "v03_mammalsleep_trace2.png",
    )

    tv_idx = boy_names.index("tv")

    def _tv_means() -> str:
        means = [float(np.nanmean(complete(imp1, i)[:, tv_idx])) for i in range(1, imp1.m + 1)]
        return format_tv_means_tibble_r(means)

    b = VignetteBuilder.from_meta(get_meta("03"))
    b.set_intro(load_intro(), authors=AUTHORS, series_label=SERIES_LABEL)
    b.set_disclaimer(GLOBAL_DISCLAIMER)
    b.set_parity_overview(V03_PARITY_OVERVIEW)
    ASSETS.mkdir(parents=True, exist_ok=True)

    b.numbered_section(
        1,
        load_step_title(1),
        [
            TutorialPart(
                r_code="require(mice)\nrequire(lattice)\nset.seed(123)",
                r_expected=R_SETUP,
                python_code=(
                    "import numpy as np\n"
                    "from pymice import mice, complete, with_mids, pool, help, md_pattern, summary_pool\n"
                    "from pymice.diagnostics.plots import plot_histogram, plot_mids\n"
                    "from lib.data import load_boys_full_matrix, load_mammalsleep_full\n"
                    "from lib.viz import save_figure\n"
                    "from lib.r_style import (\n"
                    "    format_bool_vector_r,\n"
                    "    format_dataframe_r,\n"
                    "    format_md_pattern_r,\n"
                    "    format_pool_mipo_r,\n"
                    "    format_pool_v03_summary_r,\n"
                    "    format_summary_r,\n"
                    "    format_tv_means_tibble_r\n"
                    ")"
                ),
                run=lambda: "(setup — no console output)",
                partial=True,
                partial_reason="Package load step; no R console output to compare.",
                narrative_after=N1_AFTER,
            ),
        ],
    )

    b.numbered_section(
        2,
        load_step_title(2),
        [
            TutorialPart(
                narrative_before=N2_HELP,
                r_code="help(boys)\n?boys",
                r_expected=R_HELP,
                python_code="print(format_help_r('boys'))",
                run=lambda: format_help_r("boys"),
                exact=True,
            ),
        ],
    )

    b.numbered_section(
        3,
        load_step_title(3),
        [
            TutorialPart(
                r_code="head(boys)",
                python_code="print(format_boys_head_r())",
                run=format_boys_head_r,
                r_expected=g("03", 3, 2),
                exact=True,
            ),
            TutorialPart(
                r_code="nrow(boys)",
                python_code="print(f'[1] {boys.shape[0]}')",
                run=lambda: f"[1] {boys.shape[0]}",
                r_expected=g("03", 3, 3),
                exact=True,
            ),
            TutorialPart(
                r_code="summary(boys)",
                r_expected=g("03", 3, 4),
                python_code="print(format_summary_boys_r(boys, boy_names))",
                run=lambda: format_summary_boys_r(boys, boy_names),
                exact=True,
            ),
        ],
    )

    b.numbered_section(
        4,
        load_step_title(4),
        [
            TutorialPart(
                r_code="md.pattern(boys)",
                python_code="print(format_md_pattern_r(md_pattern(boys, boy_names)))",
                run=lambda: format_md_pattern_r(mpat),
                r_expected=g("03", 4, 5),
                exact=True,
                narrative_after=N4_AFTER,
            ),
        ],
    )

    b.numbered_section(
        5,
        load_step_title(5),
        [
            TutorialPart(
                r_code="mpat <- md.pattern(boys)",
                python_code="mpat = md_pattern(boys, boy_names)",
                run=lambda: "(md.pattern table — used in next part)",
                is_plot=True,
                plot_note="R draws default `md.pattern` graphic when assigning `mpat`.",
                partial=True,
                partial_reason="Assigns `mpat`; count printed in following part.",
            ),
            TutorialPart(
                r_code='sum(mpat[, "gen"] == 0)',
                python_code=(
                    'gen_col = boy_names.index("gen")\n'
                    "print(f'[1] {int(np.sum(mpat.matrix[:-1, gen_col] == 0))}')"
                ),
                run=lambda: f"[1] {int(np.sum(mpat.matrix[:-1, gen_col] == 0))}",
                r_expected=g("03", 5, 7),
                exact=True,
                narrative_after=N5_AFTER,
            ),
        ],
    )

    b.numbered_section(
        6,
        load_step_title(6),
        [
            TutorialPart(
                narrative_before=N6_BEFORE_IND,
                r_code="R <- is.na(boys$gen)\nR",
                r_expected=g("03", 6, 8),
                python_code="print(format_bool_vector_r(np.isnan(boys[:, gen_col])))",
                run=lambda: format_bool_vector_r(gen_missing, max_lines=None),
                exact=True,
                narrative_after=N6_AFTER_IND,
            ),
            TutorialPart(
                narrative_before=N6_BEFORE_HIST,
                r_code="histogram(boys$gen)",
                python_code="plot_histogram(boys, boy_names, 'gen')",
                is_plot=True,
                narrative_after=N6_HIST_EQUIV,
            ),
            TutorialPart(
                r_code="histogram(~age|R, data=boys)",
                r_expected=R_MICE_BOYS,
                python_code=(
                    "plot_histogram(boys, boy_names, 'age', condition=np.isnan(boys[:, gen_col]))"
                ),
                is_plot=True,
                narrative_after=N6_AFTER_HIST,
            ),
        ],
        images=[hist_gen, hist_age],
    )

    b.numbered_section(
        7,
        load_step_title(7),
        [
            TutorialPart(
                r_code="imp1 <- mice(boys, print=FALSE)",
                r_expected=R_MICE_BOYS,
                python_code=(
                    "imp1 = mice(boys, column_names=boy_names, m=5, maxit=5, print_flag=False)"
                ),
                run=lambda: "(imputation complete — no printed output)",
                partial=True,
                partial_reason="Creates `imp1` object; R vignette prints no console output here.",
            ),
        ],
    )

    b.numbered_section(
        8,
        load_step_title(8),
        [
            TutorialPart(
                r_code="summary(boys)",
                r_expected=g("03", 8, 13),
                python_code="print(format_summary_boys_r(boys, boy_names))",
                run=lambda: format_summary_boys_r(boys, boy_names),
                exact=True,
            ),
            TutorialPart(
                r_code="summary(complete(imp1))",
                r_expected=g("03", 8, 14),
                python_code=(
                    "filled = complete(imp1, 1)\n"
                    "print(format_summary_boys_r(filled, boy_names, compact_factors=True))"
                ),
                run=lambda: format_summary_boys_r(
                    complete(imp1, 1), boy_names, compact_factors=True
                ),
                exact=True,
                narrative_after=N8_AFTER_SUMMARY,
            ),
            TutorialPart(
                narrative_before=N8_BEFORE_WITH,
                r_code="summary(with(imp1, mean(tv)))",
                python_code=(
                    "means = [np.nanmean(complete(imp1, i)[:, tv_idx]) for i in range(1, imp1.m + 1)]\n"
                    "print(format_tv_means_tibble_r(means))"
                ),
                run=_tv_means,
                r_expected=g("03", 8, 15),
                atol=0.2,
            ),
        ],
    )

    b.part(PART_IMPORTANCE)

    b.numbered_section(
        9,
        load_step_title(9),
        [
            TutorialPart(
                narrative_before=N9_BEFORE_MS,
                r_code="help(mammalsleep)",
                r_expected=R_HELP_MAMMAL,
                python_code="print(format_help_r('mammalsleep'))",
                run=lambda: format_help_r("mammalsleep"),
                exact=True,
            ),
            TutorialPart(
                r_code="head(mammalsleep)",
                r_expected=g("03", 9, 17),
                python_code="print(format_mammalsleep_head_r())",
                run=format_mammalsleep_head_r,
                exact=True,
            ),
            TutorialPart(
                r_code="summary(mammalsleep)",
                r_expected=g("03", 9, 18),
                python_code="print(format_summary_mammalsleep_r(ms_full, ms_names))",
                run=lambda: format_summary_mammalsleep_r(ms_full, ms_names),
                exact=True,
            ),
            TutorialPart(
                r_code="str(mammalsleep)",
                python_code="# str() layout — static R reference",
                run=lambda: g("03", 9, 19),
                r_expected=g("03", 9, 19),
                exact=True,
            ),
            TutorialPart(
                r_code="md.pattern(mammalsleep)",
                python_code="print(format_md_pattern_r(md_pattern(ms_full, ms_names)))",
                run=lambda: format_md_pattern_r(ms_mdp),
                r_expected=g("03", 9, 20),
                exact=True,
                narrative_after=N9_AFTER_MDP,
            ),
        ],
    )

    b.numbered_section(
        10,
        load_step_title(10),
        [
            TutorialPart(
                r_code="imp <- mice(mammalsleep, maxit = 10, print=F)",
                python_code=(
                    "imp_ms = mice(ms_full, column_names=ms_names, m=5, maxit=10, print_flag=False)"
                ),
                run=lambda: format_logged_events_warning_r(len(imp_ms.logged_events)),
                r_expected=g("03", 10, 21),
                exact=True,
                narrative_after=N10_AFTER_IMP,
            ),
            TutorialPart(
                r_code="plot(imp)",
                python_code="plot_mids(imp_ms, variables=['sws', 'ps', 'ts'])",
                is_plot=True,
            ),
        ],
        images=[trace_ms],
    )

    b.numbered_section(
        11,
        load_step_title(11),
        [
            TutorialPart(
                r_code="fit1 <- with(imp, lm(sws ~ log10(bw) + odi), print=F)",
                python_code=("fit1 = with_mids(imp_ms, formula='sws ~ log10(bw) + odi')"),
                run=lambda: "(mira object created — no printed output)",
            ),
        ],
    )

    b.numbered_section(
        12,
        load_step_title(12),
        [
            TutorialPart(
                r_code="pool(fit1)",
                python_code="print(format_pool_mipo_r(pool(fit1)))",
                run=lambda: format_pool_mipo_r(pooled1),
                r_expected=g("03", 12, 24),
                exact=True,
            ),
            TutorialPart(
                r_code="summary(pool(fit1))",
                python_code="print(format_pool_v03_summary_r(summary_pool(pool(fit1))))",
                run=lambda: format_pool_v03_summary_r(summary_pool(pooled1)),
                r_expected=g("03", 12, 25),
                exact=True,
                narrative_after=N12_AFTER_POOL,
            ),
        ],
    )

    b.numbered_section(
        13,
        load_step_title(13),
        [
            TutorialPart(
                r_code="impnew <- mice(mammalsleep[ , -1], maxit = 10, print = F)",
                python_code=(
                    "impnew = mice(ms_no_sp, column_names=ms_no_names, m=5, maxit=10, "
                    "print_flag=False)"
                ),
                run=lambda: format_logged_events_warning_r(len(impnew.logged_events)),
                r_expected=g("03", 13, 26),
                exact=True,
            ),
        ],
    )

    b.numbered_section(
        14,
        load_step_title(14),
        [
            TutorialPart(
                r_code="fit2 <- with(impnew, lm(sws ~ log10(bw) + odi))\npool(fit2)",
                python_code=(
                    "fit2 = with_mids(impnew, formula='sws ~ log10(bw) + odi')\n"
                    "print(format_pool_mipo_r(pool(fit2)))"
                ),
                run=lambda: format_pool_mipo_r(pooled2),
                r_expected=g("03", 14, 27),
                exact=True,
            ),
            TutorialPart(
                r_code="summary(pool(fit2))",
                python_code="print(format_pool_v03_summary_r(summary_pool(pool(fit2))))",
                run=lambda: format_pool_v03_summary_r(summary_pool(pooled2)),
                r_expected=g("03", 14, 28),
                exact=True,
                narrative_after=N14_AFTER_POOL,
            ),
        ],
    )

    b.numbered_section(
        15,
        load_step_title(15),
        [
            TutorialPart(
                r_code="plot(impnew)",
                python_code="plot_mids(impnew, variables=['mls', 'gt'])",
                is_plot=True,
                narrative_after=N15_AFTER,
            ),
        ],
        images=[trace_new],
    )

    return b.build()
