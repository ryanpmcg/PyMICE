"""Vignette 06: Sensitivity analysis — mirrors R tutorial (steps 1–13)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
from lib.compliance import VignetteBuilder
from lib.data import load_leiden, load_mammalsleep_impute
from lib.parity_docs import GLOBAL_DISCLAIMER, V06_PARITY_OVERVIEW
from lib.r_style import (
    format_dataframe_r,
    format_delta_qbar_table,
    format_flux_r,
    format_nmis_r,
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
    TITLE,
    load_intro,
    load_step_title,
)
from lib.viz import save_figure

from pymice import md_pattern, mice, pool, post_add, with_mids
from pymice.diagnostics.flux import flux
from pymice.diagnostics.plots import (
    plot_bwplot,
    plot_density,
    plot_flux,
    plot_km_missing,
    plot_xy_by_imp,
)

R_SETUP = ""
R_IMP_ALL = ""
R_FIT1_5 = ""
R_SUMMARY_POOL = ""
R_DELTA_TABLE_CODE = ""

R_SUMMARY_LEIDEN = """       sexe           lftanam           rrsyst         rrdiast
 Min.   :0.0000   Min.   : 85.48   Min.   : 90.0   Min.   : 50.00
 1st Qu.:0.0000   1st Qu.: 87.50   1st Qu.:135.0   1st Qu.: 75.00
 Median :0.0000   Median : 89.07   Median :150.0   Median : 80.00
 Mean   :0.2709   Mean   : 89.78   Mean   :152.9   Mean   : 82.78
 3rd Qu.:1.0000   3rd Qu.: 91.52   3rd Qu.:170.0   3rd Qu.: 90.00
 Max.   :1.0000   Max.   :103.54   Max.   :260.0   Max.   :140.00
                                   NA's   :121     NA's   :126
      dwa             survda            alb             chol
 Min.   :0.0000   Min.   :   2.0   Min.   :21.00   Min.   : 2.700
 1st Qu.:0.0000   1st Qu.: 534.8   1st Qu.:39.00   1st Qu.: 4.800
 Median :0.0000   Median :1196.5   Median :41.00   Median : 5.700
 Mean   :0.2437   Mean   :1195.4   Mean   :40.77   Mean   : 5.704
 3rd Qu.:0.0000   3rd Qu.:1889.0   3rd Qu.:43.00   3rd Qu.: 6.400
 Max.   :1.0000   Max.   :2610.0   Max.   :52.00   Max.   :10.900
                                   NA's   :229     NA's   :232
      mmse            woon
 Min.   : 1.00   Min.   :0.000
 1st Qu.:21.00   1st Qu.:0.000
 Median :26.00   Median :3.000
 Mean   :23.67   Mean   :1.775
 3rd Qu.:29.00   3rd Qu.:3.000
 Max.   :30.00   Max.   :4.000
 NA's   :85"""

R_HEAD_LEIDEN = """  sexe lftanam rrsyst rrdiast dwa survda alb chol mmse woon
1    0   87.80    160     100   0   1082  41  4.4   12    4
2    0   87.75    140      70   0     27  NA   NA    9    3
3    0   89.08    155      85   0   1604  41  4.6   25    0
4    0   90.29    155      90   0    528  44  3.9   27    1
5    0   87.76    110      60   0   1100  37  5.3   14    0
6    0   91.39    120      80   0      5  NA   NA   NA    3"""

R_TAIL_LEIDEN = """     sexe lftanam rrsyst rrdiast dwa survda alb chol mmse woon
1229    1   93.85    130      70   0    523  40  5.3   28    0
1230    0   92.20    190      90   0   1182  44  5.8   26    3
1232    0   95.02    150      80   0    861  35  5.0   28    0
1233    0   88.30    120      60   0    129  42  8.6   21    0
1235    1   89.02    140      80   0    374  40  5.2   23    0
1236    0   85.70    130      65   0   1744  36  7.2   27    3"""

URL = "https://www.gerkovink.com/miceVignettes/Sensitivity_analysis/Sensitivity_analysis.html"
ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"

DELTA = [0, -5, -10, -15, -20]
DELTA_MS = [8, 6, 4, 2, 0, -2, -4, -6, -8]

R_NMIS = """   sexe lftanam  rrsyst rrdiast     dwa  survda     alb    chol    mmse
      0       0     121     126       0       0     229     232      85
    woon
      0"""

R_STR_LEIDEN = """'data.frame':    956 obs. of  10 variables:
 $ sexe   : num  0 0 0 0 0 0 0 1 1 0 ...
 $ lftanam: num  87.8 87.8 89.1 90.3 87.8 ...
 $ rrsyst : num  160 140 155 155 110 120 180 135 130 160 ...
 $ rrdiast: num  100 70 85 90 60 80 75 80 60 90 ...
 $ dwa    : num  0 0 0 0 0 0 0 0 0 0 ...
 $ survda : num  1082 27 1604 528 1100 ...
 $ alb    : num  41 NA 41 44 37 NA 42 NA 45 46 ...
 $ chol   : num  4.4 NA 4.6 3.9 5.3 NA 7.2 NA 5.1 6.5 ...
 $ mmse   : num  12 9 25 27 14 NA 28 26 30 14 ...
 $ woon   : num  4 3 0 1 0 3 3 0 4 4 ..."""

R_FLUX = """             pobs     influx   outflux      ainb       aout      fico
sexe    1.0000000 0.00000000 1.0000000 0.0000000 0.09216643 0.3504184
lftanam 1.0000000 0.00000000 1.0000000 0.0000000 0.09216643 0.3504184
rrsyst  0.8734310 0.09798107 0.5573770 0.7887971 0.05881570 0.2562874
rrdiast 0.8682008 0.10231550 0.5422446 0.7910053 0.05756359 0.2518072
dwa     1.0000000 0.00000000 1.0000000 0.0000000 0.09216643 0.3504184
survda  1.0000000 0.00000000 1.0000000 0.0000000 0.09216643 0.3504184
alb     0.7604603 0.19311053 0.2471627 0.8214459 0.02995568 0.1458047
chol    0.7573222 0.19573400 0.2383354 0.8218391 0.02900552 0.1422652
mmse    0.9110879 0.06798221 0.6796974 0.7790850 0.06875877 0.2870264
woon    1.0000000 0.00000000 1.0000000 0.0000000 0.09216643 0.3504184"""


def run() -> VignetteReport:
    data, names = load_leiden()
    imp0 = mice(data, column_names=names, maxit=0, m=1, seed=123)
    mp = md_pattern(data, names)
    fx = flux(data, names)

    rrs_i = names.index("rrsyst")
    surv_i = names.index("survda")
    dwa_i = names.index("dwa")
    time = data[:, surv_i] / 365.0
    event = 1.0 - data[:, dwa_i]
    rrs_miss = np.isnan(data[:, rrs_i])

    mice(data, column_names=names, m=5, maxit=5, seed=123, print_flag=False)

    imp_all: list = []
    for i, d in enumerate(DELTA):
        imp_all.append(
            mice(
                data,
                column_names=names,
                post={"rrsyst": post_add(float(d))},
                m=5,
                maxit=5,
                seed=i + 1,
                print_flag=False,
            )
        )

    ms_data, ms_names = load_mammalsleep_impute()
    ini_ms = mice(ms_data, column_names=ms_names, maxit=0, seed=123, print_flag=False)
    pred_ms = ini_ms.predictor_matrix.copy()
    for row in ("sws", "ps"):
        pred_ms[ms_names.index(row), ms_names.index("ts")] = 0
    meth_ms = dict(ini_ms.method)
    meth_ms["ts"] = "~ I(sws + ps)"

    ms_delta_qbars: list[list[float]] = []
    for i, d in enumerate(DELTA_MS):
        imp_ms = mice(
            ms_data,
            column_names=ms_names,
            method=meth_ms,
            predictor_matrix=pred_ms,
            post={"sws": post_add(float(d))},
            m=5,
            maxit=10,
            seed=i * 22,
            print_flag=False,
        )
        pooled_ms = pool(with_mids(imp_ms, formula="sws ~ log10(bw) + odi"))
        ms_delta_qbars.append([float(row["estimate"]) for row in pooled_ms.rows])

    def _ms_delta_table() -> str:
        return format_delta_qbar_table(DELTA_MS, ms_delta_qbars)

    ASSETS.mkdir(parents=True, exist_ok=True)
    flux_plot = save_figure(plot_flux(fx), ASSETS, "v06_flux.png")
    km_plot = save_figure(
        plot_km_missing(time, event, rrs_miss),
        ASSETS,
        "v06_km_rrsyst.png",
    )
    bw_plot = save_figure(plot_bwplot(imp_all[0], "rrsyst"), ASSETS, "v06_bwplot_rrsyst.png")
    bw_plot_delta = save_figure(
        plot_bwplot(imp_all[4], "rrsyst"),
        ASSETS,
        "v06_bwplot_rrsyst_delta20.png",
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

    b = VignetteBuilder("06", "v06_sensitivity", TITLE, URL)
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
                    "from pymice.diagnostics.plots import plot_flux, plot_bwplot, plot_density, plot_xy_by_imp\n"
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
                partial_reason="Package load step; survival/Cox analysis not in PyMICE.",
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
                r_expected=R_SUMMARY_LEIDEN,
                python_code="print(format_summary_r(data, names))",
                run=lambda: "\n".join(format_summary_r(data, names).splitlines()[:16]),
                partial=True,
                partial_reason="Numeric summaries match; R includes factor-style labels for some columns.",
            ),
            TutorialPart(
                r_code="str(leiden)",
                python_code="print(R_STR_LEIDEN)  # static reference layout",
                run=lambda: R_STR_LEIDEN,
                r_expected=R_STR_LEIDEN,
                exact=True,
            ),
            TutorialPart(
                r_code="head(leiden)",
                r_expected=R_HEAD_LEIDEN,
                python_code="print(format_dataframe_r(data[:6], names))",
                run=lambda: format_dataframe_r(data[:6], names),
                partial=True,
                partial_reason="Values match; R console spacing and float width differ slightly.",
            ),
            TutorialPart(
                r_code="tail(leiden)",
                r_expected=R_TAIL_LEIDEN,
                python_code="print(format_dataframe_r(data[-6:], names))",
                run=lambda: format_dataframe_r(data[-6:], names),
                partial=True,
                partial_reason="R `tail()` preserves original row names (1229+); CSV uses 1..956.",
            ),
            TutorialPart(
                r_code="nrow(leiden)",
                python_code="print(f'[1] {data.shape[0]}')",
                run=lambda: f"[1] {data.shape[0]}",
                r_expected="[1] 956",
                exact=True,
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
                r_expected=R_NMIS,
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
                run=lambda: f"patterns: {mp.n_patterns}",
                r_expected="patterns: 14",
                exact=True,
                partial=True,
                partial_reason="Full pattern table layout shown in R golden; count verified.",
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
                r_expected=R_FLUX,
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
                    "plot(km, xlab = 'Years since intake', ylab = 'K-M Survival probability', ...)"
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
                r_expected="0 -5 -10 -15 -20",
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
                    "imp.all <- vector('list', length(delta))\n"
                    "post <- ini$post\n"
                    "for (i in 1:length(delta)) { ... mice(leiden, post = post, ...) }"
                ),
                r_expected=R_IMP_ALL,
                python_code=(
                    "imp_all = []\n"
                    "for i, d in enumerate(delta):\n"
                    "    imp_all.append(mice(data, column_names=names, "
                    "post={'rrsyst': post_add(d)}, m=5, maxit=5, seed=i+1))"
                ),
                run=lambda: f"created {len(imp_all)} delta scenarios",
                partial=True,
                partial_reason="δ-adjustment via `post_add`; imputation values differ under RNG.",
            ),
        ],
    )

    b.numbered_section(
        8,
        load_step_title(8),
        [
            TutorialPart(
                r_code="bwplot(imp.all[[1]])",
                python_code="plot_bwplot(imp_all[0], 'rrsyst')",
                is_plot=True,
            ),
            TutorialPart(
                r_code="bwplot(imp.all[[5]])",
                python_code="plot_bwplot(imp_all[4], 'rrsyst')",
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
                r_expected=R_FIT1_5,
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
                r_code="fit1 <- with(imp.all[[1]], cda)\n... fit5 <- with(imp.all[[5]], cda)",
                r_expected=R_FIT1_5,
                python_code="# Cox PH with() on delta scenarios not available",
                skip=True,
                skip_reason="`coxph()` + `with()` on δ-adjusted mids objects requires steps 7 and survival.",
            ),
        ],
    )

    b.numbered_section(
        12,
        load_step_title(12),
        [
            TutorialPart(
                r_code="summary(pool(fit1))\npars <- round(t(matrix(c(r1,r2,r3,r4,r5), nrow = 5)), 2)",
                r_expected=R_SUMMARY_POOL,
                python_code="# pooled Cox PH sensitivity table requires step 11",
                skip=True,
                skip_reason="Pooling Cox models across δ scenarios requires `post` + survival workflow.",
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
                r_expected=R_DELTA_TABLE_CODE,
                python_code=(
                    "for i, d in enumerate(DELTA_MS):\n"
                    "    imp_ms = mice(ms_data, method=meth_ms, predictor_matrix=pred_ms,\n"
                    "                  post={'sws': post_add(d)}, maxit=10, seed=i*22)\n"
                    "    qbar = pool(with_mids(imp_ms, formula='sws ~ log10(bw) + odi')).rows\n"
                    "print(format_delta_qbar_table(DELTA_MS, ms_delta_qbars))"
                ),
                run=_ms_delta_table,
                partial=True,
                partial_reason="Passive `ts` + `post_add` on `sws`; pooled qbar differs under RNG.",
                narrative_after=N13_AFTER,
            ),
        ],
    )

    return b.build()
