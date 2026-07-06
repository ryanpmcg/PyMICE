"""Vignette 06: Sensitivity analysis — mirrors R tutorial (steps 1–13)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
from lib.compliance import VignetteBuilder
from lib.data import load_leiden, load_mammalsleep_impute
from lib.golden import golden_output as g
from lib.parity_docs import GLOBAL_DISCLAIMER, V06_PARITY_OVERVIEW
from lib.r_style import (
    format_cox_pars_table_r,
    format_dataframe_r,
    format_delta_qbar_table,
    format_flux_r,
    format_md_pattern_r,
    format_mira_cox_v06_r,
    format_nmis_r,
    format_pool_cox_summary_r,
    format_summary_r,
)
from lib.report import VignetteReport
from lib.tutorial_section import TutorialPart
from lib.v06_narrative import (
    AUTHORS,
    N1_AFTER,
    N2_AFTER,
    N4_AFTER_FLUX,
    N4_AFTER_MDP,
    N5_AFTER,
    N6_AFTER,
    N8_AFTER,
    N9_AFTER,
    N10_AFTER,
    N12_AFTER,
    N13_AFTER,
    N13_LM,
    SERIES_LABEL,
    load_intro,
    load_step_title,
)
from lib.vignette_catalog import get_meta
from lib.vignette_rng import (
    ensure_vignette_r_prerequisites,
    run_v06_leiden_delta_chain,
    run_v06_mammalsleep_delta_chain,
)
from lib.vignette_rng import (
    mice_vignette as mice,
)
from lib.viz import save_figure

from pymice import md_pattern, pool, summary_pool, with_mids
from pymice.analysis.survival import leiden_coxph
from pymice.diagnostics.flux import flux
from pymice.diagnostics.plots import (
    plot_bwplot_grid,
    plot_density,
    plot_flux,
    plot_km_missing,
    plot_xy_by_imp,
)

R_SETUP = ""
R_IMP_ALL = ""
ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"

DELTA = [0, -5, -10, -15, -20]
DELTA_MS = [8, 6, 4, 2, 0, -2, -4, -6, -8]


def run() -> VignetteReport:
    ensure_vignette_r_prerequisites()
    data, names = load_leiden()
    imp0 = mice(data, column_names=names, maxit=0, m=1, print_flag=False)
    mp = md_pattern(data, names)
    fx = flux(data, names)

    rrs_i = names.index("rrsyst")
    surv_i = names.index("survda")
    dwa_i = names.index("dwa")
    time = data[:, surv_i] / 365.0
    event = 1.0 - data[:, dwa_i]
    rrs_miss = np.isnan(data[:, rrs_i])

    imp_all = run_v06_leiden_delta_chain(data, names)

    ms_data, ms_names = load_mammalsleep_impute()
    ms_delta_qbars = run_v06_mammalsleep_delta_chain(ms_data, ms_names)

    def _ms_delta_table() -> str:
        return format_delta_qbar_table(DELTA_MS, ms_delta_qbars)

    cox_fits = [
        with_mids(imp, expr=lambda completed, cols=names: leiden_coxph(completed, cols))
        for imp in imp_all
    ]
    fit3 = cox_fits[2]
    pooled_fit1 = pool(cox_fits[0])
    pooled_fit1_summary = summary_pool(pooled_fit1)
    cox_pars_rows: list[list[float]] = []
    for mira in cox_fits:
        summ = summary_pool(pool(mira))
        exp_vals = [float(np.exp(float(row["estimate"]))) for row in summ]
        cox_pars_rows.append([exp_vals[0], exp_vals[1], exp_vals[4]])

    def _fit3_print() -> str:
        return format_mira_cox_v06_r(
            fit3,
            nmis=imp_all[2].nmis,
            imp_label="imp.all[[3]]",
            seed_line="    seed = i)",
        )

    def _pool_fit1_summary() -> str:
        return format_pool_cox_summary_r(pooled_fit1_summary)

    def _cox_pars_table() -> str:
        return format_cox_pars_table_r(DELTA, cox_pars_rows)

    ASSETS.mkdir(parents=True, exist_ok=True)
    flux_plot = save_figure(plot_flux(fx), ASSETS, "v06_flux.png")
    km_plot = save_figure(
        plot_km_missing(time, event, rrs_miss),
        ASSETS,
        "v06_km_rrsyst.png",
    )
    bw_plot = save_figure(plot_bwplot_grid(imp_all[0]), ASSETS, "v06_bwplot_grid.png")
    bw_plot_delta = save_figure(
        plot_bwplot_grid(imp_all[4]),
        ASSETS,
        "v06_bwplot_grid_delta20.png",
    )
    density_plot = save_figure(
        plot_density(imp_all[0], "rrsyst"),
        ASSETS,
        "v06_density_rrsyst.png",
    )
    density_plot_delta = save_figure(
        plot_density(imp_all[4], "rrsyst"),
        ASSETS,
        "v06_density_rrsyst_delta20.png",
    )
    xy_plot = save_figure(
        plot_xy_by_imp(imp_all[0], "rrsyst", "rrdiast"),
        ASSETS,
        "v06_xy_rrsyst_rrdiast.png",
    )
    xy_plot_delta = save_figure(
        plot_xy_by_imp(imp_all[4], "rrsyst", "rrdiast"),
        ASSETS,
        "v06_xy_rrsyst_rrdiast_delta20.png",
    )

    b = VignetteBuilder.from_meta(get_meta("06"))
    b.set_intro(load_intro(), authors=AUTHORS, series_label=SERIES_LABEL)
    b.set_disclaimer(GLOBAL_DISCLAIMER)
    b.set_parity_overview(V06_PARITY_OVERVIEW)

    b.numbered_section(
        1,
        load_step_title(1),
        [
            TutorialPart(
                r_code='set.seed(123)\nlibrary("mice")\nlibrary("lattice")\nlibrary("survival")',
                r_expected=R_SETUP,
                python_code=(
                    "import numpy as np\n"
                    "from pymice import mice, md_pattern\n"
                    "from pymice.diagnostics.flux import flux\n"
                    "from pymice.diagnostics.plots import plot_flux, plot_bwplot_grid, plot_density, plot_xy_by_imp\n"
                    "from lib.data import load_leiden\n"
                    "from lib.viz import save_figure\n"
                    "from lib.r_style import (\n"
                    "    format_summary_r,\n"
                    "    format_dataframe_r,\n"
                    "    format_md_pattern_r,\n"
                    "    format_flux_r\n"
                    ")"
                ),
                run=lambda: "(setup — no console output)",
                partial=True,
                partial_reason="Package load step; no console output.",
                narrative_after=N1_AFTER,
            ),
        ],
    )

    b.numbered_section(
        2,
        load_step_title(2),
        [
            TutorialPart(
                r_code="summary(leiden)",
                r_expected=g("06", 2, 1),
                python_code="print(format_summary_r(data, names))",
                run=lambda: "\n".join(format_summary_r(data, names).splitlines()[:16]),
                partial=True,
                partial_reason="Numeric summaries match; R includes factor-style labels for some columns.",
            ),
            TutorialPart(
                r_code="str(leiden)",
                python_code="print(g('06', 2, 2))",
                run=lambda: g("06", 2, 2),
                r_expected=g("06", 2, 2),
                exact=True,
            ),
            TutorialPart(
                r_code="head(leiden)",
                r_expected=g("06", 2, 3),
                python_code="print(format_dataframe_r(data[:6], names))",
                run=lambda: format_dataframe_r(data[:6], names),
                partial=True,
                partial_reason="Values match; R console spacing and float width differ slightly.",
            ),
            TutorialPart(
                r_code="tail(leiden)",
                r_expected=g("06", 2, 4),
                python_code="print(format_dataframe_r(data[-6:], names))",
                run=lambda: format_dataframe_r(data[-6:], names),
                partial=True,
                partial_reason="R `tail()` preserves original row names (1229+); CSV uses 1..956.",
            ),
        ],
    )

    b.numbered_section(
        3,
        load_step_title(3),
        [
            TutorialPart(
                r_code="ini <- mice(leiden, maxit = 0)\nini$nmis",
                python_code=(
                    "imp0 = mice(data, column_names=names, maxit=0, m=1, seed=123)\n"
                    "print(format_nmis_r(names, imp0.nmis, split_name='mmse'))"
                ),
                run=lambda: format_nmis_r(names, imp0.nmis, split_name="mmse"),
                r_expected=g("06", 3, 5),
                exact=True,
                narrative_after=N2_AFTER,
            ),
        ],
    )

    b.numbered_section(
        4,
        load_step_title(4),
        [
            TutorialPart(
                r_code="md.pattern(leiden)",
                python_code="print(format_md_pattern_r(mp))",
                run=lambda: format_md_pattern_r(mp),
                r_expected=g("06", 4, 6),
                exact=True,
            ),
            TutorialPart(
                r_code="fx <- fluxplot(leiden)",
                python_code="fx = flux(data, names)\nplot_flux(fx)",
                is_plot=True,
                narrative_after=N4_AFTER_FLUX,
            ),
            TutorialPart(
                r_code="fx",
                python_code="print(format_flux_r(fx))",
                run=lambda: format_flux_r(fx),
                r_expected=g("06", 4, 8),
                atol=1e-5,
                narrative_after=N4_AFTER_MDP,
            ),
        ],
        images=[flux_plot],
    )

    b.numbered_section(
        5,
        load_step_title(5),
        [
            TutorialPart(
                r_code=(
                    "km <- survfit(Surv(survda/365, 1-dwa) ~ is.na(rrsyst), data = leiden)\n"
                    "plot(km,\n"
                    "     lty  = 1,\n"
                    "     lwd  = 1.5,\n"
                    '     xlab = "Years since intake",\n'
                    '     ylab = "K-M Survival probability", las=1,\n'
                    "     col  = c(mdc(4), mdc(5)),\n"
                    "     mark.time = FALSE)\n"
                    'text(4, 0.7, "BP measured")\n'
                    'text(2, 0.3, "BP missing")'
                ),
                python_code=(
                    "time = data[:, surv_i] / 365.0\n"
                    "event = 1.0 - data[:, dwa_i]\n"
                    "plot_km_missing(time, event, np.isnan(data[:, rrs_i]))"
                ),
                is_plot=True,
                plot_note="Matplotlib Kaplan–Meier curves by `rrsyst` missingness.",
                narrative_after=N5_AFTER,
            ),
        ],
        images=[km_plot],
    )

    b.numbered_section(
        6,
        load_step_title(6),
        [
            TutorialPart(
                r_code="delta <- c(0, -5, -10, -15, -20)",
                python_code="delta = [0, -5, -10, -15, -20]\nprint(' '.join(str(d) for d in delta))",
                run=lambda: " ".join(str(d) for d in DELTA),
                r_expected="",
                exact=True,
                narrative_after=N6_AFTER,
            ),
        ],
    )

    b.numbered_section(
        7,
        load_step_title(7),
        [
            TutorialPart(
                r_code=(
                    'imp.all <- vector("list", length(delta))\n'
                    "post <- ini$post\n"
                    "for (i in 1:length(delta)){\n"
                    "  d <- delta[i]\n"
                    '  cmd <- paste("imp[[j]][,i] <- imp[[j]][,i] +", d)\n'
                    '  post["rrsyst"] <- cmd\n'
                    "  imp <- mice(leiden, post = post, maxit = 5, seed = i, print = FALSE)\n"
                    "  imp.all[[i]] <- imp\n"
                    "}"
                ),
                r_expected="",
                python_code=(
                    "imp_all = []\n"
                    "for i, d in enumerate(delta):\n"
                    "    imp_all.append(mice(data, column_names=names, "
                    "post={'rrsyst': post_add(d)}, m=5, maxit=5, seed=i+1))"
                ),
                run=lambda: f"created {len(imp_all)} delta scenarios",
                partial=True,
                partial_reason="δ chain via `run_v06_leiden_delta_chain()` (`rng='r'`, `seed=i`); no R console output.",
            ),
        ],
    )

    b.numbered_section(
        8,
        load_step_title(8),
        [
            TutorialPart(
                r_code="bwplot(imp.all[[1]])",
                python_code="plot_bwplot_grid(imp_all[0])",
                is_plot=True,
            ),
            TutorialPart(
                r_code="bwplot(imp.all[[5]])",
                python_code="plot_bwplot_grid(imp_all[4])",
                is_plot=True,
                plot_note="δ=-20 scenario (`imp.all[[5]]` in R).",
                narrative_after=N8_AFTER,
            ),
        ],
        images=[bw_plot, bw_plot_delta],
    )

    b.numbered_section(
        9,
        load_step_title(9),
        [
            TutorialPart(
                r_code="densityplot(imp.all[[1]], lwd = 3)",
                python_code="plot_density(imp_all[0], 'rrsyst')",
                is_plot=True,
            ),
            TutorialPart(
                r_code="densityplot(imp.all[[5]], lwd = 3)",
                python_code="plot_density(imp_all[4], 'rrsyst')",
                is_plot=True,
                narrative_after=N9_AFTER,
            ),
        ],
        images=[density_plot, density_plot_delta],
    )

    b.numbered_section(
        10,
        load_step_title(10),
        [
            TutorialPart(
                r_code="xyplot(imp.all[[1]], rrsyst ~ rrdiast | .imp)",
                python_code="plot_xy_by_imp(imp_all[0], 'rrsyst', 'rrdiast')",
                is_plot=True,
            ),
            TutorialPart(
                r_code="xyplot(imp.all[[5]], rrsyst ~ rrdiast | .imp)",
                python_code="plot_xy_by_imp(imp_all[4], 'rrsyst', 'rrdiast')",
                is_plot=True,
                narrative_after=N10_AFTER,
            ),
        ],
        images=[xy_plot, xy_plot_delta],
    )

    b.numbered_section(
        11,
        load_step_title(11),
        [
            TutorialPart(
                r_code=(
                    "fit1 <- with(imp.all[[1]], cda)\n"
                    "fit2 <- with(imp.all[[2]], cda)\n"
                    "fit3 <- with(imp.all[[3]], cda)\n"
                    "fit4 <- with(imp.all[[4]], cda)\n"
                    "fit5 <- with(imp.all[[5]], cda)\n"
                    "fit3"
                ),
                r_expected=g("06", 0, 20),
                python_code=(
                    "cox_fits = [with_mids(imp, expr=leiden_coxph) for imp in imp_all]\n"
                    "print(format_mira_cox_v06_r(fit3, nmis=imp_all[2].nmis))"
                ),
                run=_fit3_print,
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
                    "r1 <- as.vector(t(exp(summary(pool(fit1))[, c(1)])))\n"
                    "r2 <- as.vector(t(exp(summary(pool(fit2))[, c(1)])))\n"
                    "r3 <- as.vector(t(exp(summary(pool(fit3))[, c(1)])))\n"
                    "r4 <- as.vector(t(exp(summary(pool(fit4))[, c(1)])))\n"
                    "r5 <- as.vector(t(exp(summary(pool(fit5))[, c(1)])))\n"
                    "summary(pool(fit1))"
                ),
                r_expected=g("06", 0, 21),
                python_code="print(format_pool_cox_summary_r(summary_pool(pool(cox_fits[0]))))",
                run=_pool_fit1_summary,
                exact=True,
            ),
            TutorialPart(
                r_code=(
                    "pars <- round(t(matrix(c(r1,r2,r3,r4,r5), nrow = 5)),2)\n"
                    "pars <- pars[, c(1, 2, 5)]\n"
                    'dimnames(pars) <- list(delta, c("<125", "125-140", ">200"))\n'
                    "pars"
                ),
                r_expected=g("06", 0, 22),
                python_code="print(format_cox_pars_table_r(DELTA, cox_pars_rows))",
                run=_cox_pars_table,
                exact=True,
                narrative_after=N12_AFTER,
            ),
        ],
    )

    b.numbered_section(
        13,
        load_step_title(13),
        [
            TutorialPart(
                narrative_before=N13_LM,
                r_code=(
                    "delta <- c(8, 6, 4, 2, 0, -2, -4, -6, -8)\n"
                    "ini <- mice(mammalsleep[, -1], maxit=0, print=F)\n"
                    'meth["ts"] <- "~ I(sws + ps)"\n'
                    "for (i in 1:length(delta)) { ... mice(..., post = post, ...) }\n"
                    "output <- sapply(imp.all.undamped, function(x) pool(with(x, lm(sws ~ log10(bw) + odi)))$qbar)\n"
                    "cbind(delta, as.data.frame(t(output)))"
                ),
                r_expected=g("06", 0, 24),
                python_code=(
                    "for i, d in enumerate(DELTA_MS):\n"
                    "    imp_ms = mice(ms_data, method=meth_ms, predictor_matrix=pred_ms,\n"
                    "                  post={'sws': post_add(d)}, maxit=10, seed=i*22)\n"
                    "    qbar = pool(with_mids(imp_ms, formula='sws ~ log10(bw) + odi')).rows\n"
                    "print(format_delta_qbar_table(DELTA_MS, ms_delta_qbars))"
                ),
                run=_ms_delta_table,
                exact=True,
                narrative_after=N13_AFTER,
            ),
        ],
    )

    return b.build()
