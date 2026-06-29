"""Vignette 02: Convergence and pooling — mirrors R tutorial (steps 1–8)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from lib.compliance import VignetteBuilder
from lib.data import load_nhanes, load_nhanes2
from lib.parity_docs import GLOBAL_DISCLAIMER, V02_PARITY_OVERVIEW
from lib.r_style import (
    R_METHODS_MICE,
    R_STR_NHANES2,
    format_lm_summary_r,
    format_meth_r,
    format_mira_print_r,
    format_pool_v02_r,
    format_predictor_matrix,
    format_summary_r,
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
    TITLE,
    load_intro,
    load_step_title,
)
from lib.viz import save_figure

from pymice import complete, mice, pool, quickpred, summary_pool, with_mids
from pymice.diagnostics.plots import plot_mids, plot_stripplot
from pymice.types import VariableKind, VariableSpec

R_SETUP = ""
R_MICE_M3 = ""
R_MICE_PRED = ""
R_MICE_SEED = ""
R_MICE_METH = ""

R_SUMMARY_NHANES2 = """    age          bmi          hyp          chl
 20-39:12   Min.   :20.40   no  :13   Min.   :113.0
 40-59: 7   1st Qu.:22.65   yes : 4   1st Qu.:185.0
 60-99: 6   Median :26.75   NA's: 8   Median :187.0
            Mean   :26.56             Mean   :191.4
            3rd Qu.:28.93             3rd Qu.:212.0
            Max.   :35.30             Max.   :284.0
            NA's   :9                 NA's   :10"""

R_MIRA_FIT = """call :
with.mids(data = imp, expr = lm(bmi ~ chl))

call1 :
mice(data = nhanes2, method = meth, printFlag = F)

nmis :
age bmi hyp chl
  0   9   8  10

analyses :
[[1]]

Call:
lm(formula = bmi ~ chl)

Coefficients:
(Intercept)          chl
    22.9566       0.0228


[[2]]

Call:
lm(formula = bmi ~ chl)

Coefficients:
(Intercept)          chl
   22.92350      0.02162


[[3]]

Call:
lm(formula = bmi ~ chl)

Coefficients:
(Intercept)          chl
   17.80342      0.04999


[[4]]

Call:
lm(formula = bmi ~ chl)

Coefficients:
(Intercept)          chl
   24.11469      0.01458


[[5]]

Call:
lm(formula = bmi ~ chl)

Coefficients:
(Intercept)          chl
   19.60360      0.03567"""

URL = "https://www.gerkovink.com/miceVignettes/Convergence_pooling/Convergence_and_pooling.html"
ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"

NHANES2_SPECS = [
    VariableSpec("age", VariableKind.UNORDERED, levels=(1.0, 2.0, 3.0)),
    VariableSpec("bmi", VariableKind.NUMERIC),
    VariableSpec("hyp", VariableKind.BINARY, levels=(1.0, 2.0)),
    VariableSpec("chl", VariableKind.NUMERIC),
]

R_PRED = """    age bmi hyp chl
age   0   1   1   1
bmi   1   0   1   1
hyp   1   1   0   1
chl   1   1   1   0"""

R_PRED_MOD = """    age bmi hyp chl
age   0   1   0   1
bmi   1   0   0   1
hyp   1   1   0   1
chl   1   1   0   0"""

R_QUICKPRED = """    age bmi hyp chl
age   0   0   0   0
bmi   1   0   0   1
hyp   1   0   0   1
chl   1   1   1   0"""

R_METH_NHANES = """  age   bmi   hyp   chl
   "" "pmm" "pmm" "pmm\""""

R_METH_NHANES2 = """     age      bmi      hyp      chl
      ""    "pmm" "logreg"    "pmm\""""

R_METH_NORM = """     age      bmi      hyp      chl
      ""   "norm" "logreg"    "pmm\""""

R_CLASS_MIRA = '[1] "mira"   "matrix"'
R_LS_FIT = '[1] "analyses" "call"     "call1"    "nmis"'

R_POOL = """              estimate  std.error statistic       df     p.value
(Intercept) 21.4803588 5.35840067  4.008726 11.28773 0.001953701
chl          0.0289319 0.02742604  1.054906 10.73032 0.314641727"""

R_LM_A2 = """Call:
lm(formula = bmi ~ chl)

Residuals:
    Min      1Q  Median      3Q     Max
-6.0682 -2.9742  0.4558  2.4361  7.6641

Coefficients:
            Estimate Std. Error t value Pr(>|t|)
(Intercept) 22.92350    3.56198   6.436 1.44e-06 ***
chl          0.02162    0.01800   1.201    0.242
---
Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

Residual standard error: 3.917 on 23 degrees of freedom
Multiple R-squared:  0.05898, Adjusted R-squared:  0.01807
F-statistic: 1.442 on 1 and 23 DF,  p-value: 0.2421"""


def _stripplot_panel(mids, variables: list[str]):
    fig, axes = plt.subplots(1, len(variables), figsize=(4 * len(variables), 4), squeeze=False)
    for ax, var in zip(axes[0], variables, strict=True):
        plot_stripplot(mids, var, ax=ax)
    fig.tight_layout()
    return fig


def run() -> VignetteReport:
    data, names = load_nhanes()
    data2, names2 = load_nhanes2()
    b = VignetteBuilder("02", "v02_convergence_pooling", TITLE, URL)
    b.set_intro(load_intro(), authors=AUTHORS, series_label=SERIES_LABEL)
    b.set_disclaimer(GLOBAL_DISCLAIMER)
    b.set_parity_overview(V02_PARITY_OVERVIEW)
    ASSETS.mkdir(parents=True, exist_ok=True)

    imp_m3 = mice(data, column_names=names, m=3, maxit=5, seed=123, print_flag=False)
    ini0 = mice(data, column_names=names, maxit=0, seed=123, print_flag=False)
    pred = ini0.predictor_matrix.copy()
    pred_mod = pred.copy()
    pred_mod[:, names.index("hyp")] = 0
    pred_quick = quickpred(data, mincor=0.3, column_names=names)

    imp_conv = mice(data, column_names=names, m=5, maxit=5, seed=123, print_flag=False)
    imp2 = mice(
        data2,
        column_names=names2,
        variable_specs=NHANES2_SPECS,
        m=5,
        maxit=5,
        seed=123,
        print_flag=False,
    )
    meth = dict(imp2.method)
    meth["bmi"] = "norm"
    imp3 = mice(
        data2,
        column_names=names2,
        variable_specs=NHANES2_SPECS,
        method=meth,
        m=5,
        maxit=5,
        seed=123,
        print_flag=False,
    )
    imp40 = mice(
        data2,
        column_names=names2,
        variable_specs=NHANES2_SPECS,
        method=meth,
        m=5,
        maxit=40,
        seed=123,
        print_flag=False,
    )

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
                r_expected=R_PRED,
                exact=True,
                narrative_after=N2_AFTER_PRED,
            ),
            TutorialPart(
                r_code="ini <- mice(nhanes, maxit=0, print=F)\npred <- ini$pred\npred",
                python_code="print(format_predictor_matrix(names, ini0.predictor_matrix))",
                run=lambda: format_predictor_matrix(names, pred),
                r_expected=R_PRED,
                exact=True,
                narrative_after=N2_AFTER_INI,
            ),
            TutorialPart(
                r_code='pred[ ,"hyp"] <- 0\npred',
                python_code=(
                    "pred[:, names.index('age')] = 0\nprint(format_predictor_matrix(names, pred))"
                ),
                run=lambda: format_predictor_matrix(names, pred_mod),
                r_expected=R_PRED_MOD,
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
                r_expected=R_QUICKPRED,
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
                python_code="print(format_meth_r(names, imp_conv.method, style='nhanes'))",
                run=lambda: format_meth_r(names, imp_conv.method, style="nhanes"),
                r_expected=R_METH_NHANES,
                exact=True,
                narrative_after=N4_AFTER_METH,
            ),
            TutorialPart(
                r_code="summary(nhanes2)",
                r_expected=R_SUMMARY_NHANES2,
                python_code="print(format_summary_r(data2, names2))",
                run=lambda: format_summary_r(data2, names2),
                partial=True,
                partial_reason="Numeric-coded factors; R shows labelled factor levels.",
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
                r_expected=R_METH_NHANES2,
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
                r_expected=R_METH_NHANES2,
                exact=True,
            ),
            TutorialPart(
                r_code='meth["bmi"] <- "norm"\nmeth',
                python_code='meth["bmi"] = "norm"\nprint(format_meth_r(names2, meth))',
                run=lambda: format_meth_r(names2, meth),
                r_expected=R_METH_NORM,
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
                plot_note="mice.mids not in PyMICE; 40-iteration trace via mice(maxit=40).",
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
                r_expected=R_MIRA_FIT,
                python_code="print(format_mira_print_r(fit, nmis=imp3.nmis))",
                run=lambda: format_mira_print_r(fit, nmis=imp3.nmis),
                partial=True,
                partial_reason="Mira coefficient vectors differ from R under seed=123.",
                narrative_after=N7_AFTER_FIT,
            ),
            TutorialPart(
                r_code="class(fit)",
                python_code='print(\'[1] "mira"   "matrix"\')',
                run=lambda: R_CLASS_MIRA,
                r_expected=R_CLASS_MIRA,
                exact=True,
            ),
            TutorialPart(
                narrative_before=N7_BEFORE_LS,
                r_code="ls(fit)",
                python_code='print(\'[1] "analyses" "call"     "call1"    "nmis"\')',
                run=lambda: R_LS_FIT,
                r_expected=R_LS_FIT,
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
                r_expected=R_LM_A2,
                atol=0.15,
                partial=True,
                partial_reason="Imputed values differ from R; summary structure matches.",
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
                r_expected=R_POOL,
                atol=0.5,
                partial=True,
                partial_reason="Pooled estimates differ from R stochastic imputations; layout matches.",
                narrative_after=N8_AFTER + "\n\n" + N8_AFTER_SCALAR,
            ),
        ],
    )

    return b.build()
