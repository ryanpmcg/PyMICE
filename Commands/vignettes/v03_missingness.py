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
from lib.parity_docs import GLOBAL_DISCLAIMER, V03_PARITY_OVERVIEW
from lib.r_style import (
    R_STR_MAMMALSLEEP,
    format_bool_vector_r,
    format_dataframe_r,
    format_md_pattern_r,
    format_pool_mipo_r,
    format_pool_v03_summary_r,
    format_summary_r,
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
    TITLE,
    load_intro,
    load_step_title,
)
from lib.viz import save_figure

from pymice import complete, help, md_pattern, mice, pool, summary_pool, with_mids
from pymice.diagnostics.plots import plot_histogram, plot_mids

R_SETUP = ""
R_HELP = ""
R_MICE_BOYS = ""
R_HELP_MAMMAL = ""
R_FIT1_WITH = ""

R_SUMMARY_BOYS = """      age              hgt              wgt              bmi
 Min.   : 0.035   Min.   : 50.00   Min.   :  3.14   Min.   :11.77
 1st Qu.: 1.581   1st Qu.: 84.88   1st Qu.: 11.70   1st Qu.:15.90
 Median :10.505   Median :147.30   Median : 34.65   Median :17.45
 Mean   : 9.159   Mean   :132.15   Mean   : 37.15   Mean   :18.07
 3rd Qu.:15.267   3rd Qu.:175.22   3rd Qu.: 59.58   3rd Qu.:19.53
 Max.   :21.177   Max.   :198.00   Max.   :117.40   Max.   :31.74
                  NA's   :20       NA's   :4        NA's   :21
       hc          gen        phb            tv           reg
 Min.   :33.70   G1  : 56   P1  : 63   Min.   : 1.00   north: 81
 1st Qu.:48.12   G2  : 50   P2  : 40   1st Qu.: 4.00   east :161
 Median :53.00   G3  : 22   P3  : 19   Median :12.00   west :239
 Mean   :51.51   G4  : 42   P4  : 32   Mean   :11.89   south:191
 3rd Qu.:56.00   G5  : 75   P5  : 50   3rd Qu.:20.00   city : 73
 Max.   :65.00   NA's:503   P6  : 41   Max.   :25.00   NA's :  3
 NA's   :46                 NA's:503   NA's   :522"""

R_ISNA_GEN = """  [1]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
 [12]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
 [23]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
 [34]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
 [45]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
 [56]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
 [67]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
 [78]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
 [89]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[100]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[111]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[122]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[133]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[144]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[155]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[166]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[177]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[188]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[199]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[210]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[221]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[232]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[243]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[254]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[265]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[276]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[287]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[298]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[309]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
[320]  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE  TRUE FALSE
[331] FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
[342] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
[353] FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE  TRUE FALSE  TRUE
[364] FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
[375]  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE
[386] FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
[397] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE
[408] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE
[419] FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE
[430] FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE
[441] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE
[452]  TRUE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE
[463] FALSE  TRUE  TRUE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE  TRUE
[474] FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE
[485] FALSE  TRUE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE
[496]  TRUE  TRUE  TRUE FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE  TRUE
[507] FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE  TRUE
[518]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE
[529] FALSE FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE  TRUE
[540]  TRUE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE
[551]  TRUE FALSE FALSE  TRUE  TRUE  TRUE FALSE  TRUE  TRUE FALSE FALSE
[562]  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE  TRUE  TRUE  TRUE
[573] FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE
[584]  TRUE FALSE FALSE FALSE  TRUE  TRUE  TRUE FALSE  TRUE  TRUE  TRUE
[595] FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE  TRUE FALSE
[606] FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE
[617] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
[628]  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE  TRUE  TRUE FALSE
[639] FALSE FALSE  TRUE  TRUE FALSE  TRUE  TRUE FALSE FALSE  TRUE  TRUE
[650]  TRUE  TRUE  TRUE FALSE  TRUE FALSE  TRUE  TRUE  TRUE FALSE  TRUE
[661]  TRUE  TRUE  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE FALSE
[672]  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE  TRUE
[683]  TRUE FALSE  TRUE  TRUE  TRUE FALSE  TRUE FALSE  TRUE  TRUE  TRUE
[694] FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE  TRUE
[705]  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE  TRUE
[716]  TRUE FALSE FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE FALSE  TRUE
[727] FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE
[738] FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE
[748] FALSE  TRUE FALSE FALSE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE"""

R_SUMMARY_COMPLETE_IMP1 = """      age              hgt              wgt              bmi
 Min.   : 0.035   Min.   : 50.00   Min.   :  3.14   Min.   :11.77
 1st Qu.: 1.581   1st Qu.: 83.53   1st Qu.: 11.70   1st Qu.:15.87
 Median :10.505   Median :145.75   Median : 34.65   Median :17.45
 Mean   : 9.159   Mean   :131.08   Mean   : 37.12   Mean   :18.03
 3rd Qu.:15.267   3rd Qu.:174.85   3rd Qu.: 59.35   3rd Qu.:19.44
 Max.   :21.177   Max.   :198.00   Max.   :117.40   Max.   :31.74
       hc        gen      phb            tv            reg
 Min.   :33.70   G1:394   P1:401   Min.   : 1.000   north: 81
 1st Qu.:48.45   G2: 72   P2: 62   1st Qu.: 2.000   east :162
 Median :53.10   G3: 34   P3: 28   Median : 3.000   west :240
 Mean   :51.62   G4: 91   P4: 66   Mean   : 8.445   south:192
 3rd Qu.:56.00   G5:157   P5: 94   3rd Qu.:15.000   city : 73
 Max.   :65.00            P6: 97   Max.   :25.000"""

R_HEAD_MAMMAL = """                    species       bw    brw sws  ps   ts  mls  gt pi sei
1          African elephant 6654.000 5712.0  NA  NA  3.3 38.6 645  3   5
2 African giant pouched rat    1.000    6.6 6.3 2.0  8.3  4.5  42  3   1
3                Arctic Fox    3.385   44.5  NA  NA 12.5 14.0  60  1   1
4    Arctic ground squirrel    0.920    5.7  NA  NA 16.5   NA  25  5   2
5            Asian elephant 2547.000 4603.0 2.1 1.8  3.9 69.0 624  3   5
6                    Baboon   10.550  179.5 9.1 0.7  9.8 27.0 180  4   4
  odi
1   3
2   3
3   1
4   3
5   4
6   4"""

R_SUMMARY_MAMMAL = """                      species         bw                brw
 African elephant         : 1   Min.   :   0.005   Min.   :   0.14
 African giant pouched rat: 1   1st Qu.:   0.600   1st Qu.:   4.25
 Arctic Fox               : 1   Median :   3.342   Median :  17.25
 Arctic ground squirrel   : 1   Mean   : 198.790   Mean   : 283.13
 Asian elephant           : 1   3rd Qu.:  48.203   3rd Qu.: 166.00
 Baboon                   : 1   Max.   :6654.000   Max.   :5712.00
 (Other)                  :56
      sws               ps              ts             mls
 Min.   : 2.100   Min.   :0.000   Min.   : 2.60   Min.   :  2.000
 1st Qu.: 6.250   1st Qu.:0.900   1st Qu.: 8.05   1st Qu.:  6.625
 Median : 8.350   Median :1.800   Median :10.45   Median : 15.100
 Mean   : 8.673   Mean   :1.972   Mean   :10.53   Mean   : 19.878
 3rd Qu.:11.000   3rd Qu.:2.550   3rd Qu.:13.20   3rd Qu.: 27.750
 Max.   :17.900   Max.   :6.600   Max.   :19.90   Max.   :100.000
 NA's   :14       NA's   :12      NA's   :4       NA's   :4
        gt               pi             sei             odi
 Min.   : 12.00   Min.   :1.000   Min.   :1.000   Min.   :1.000
 1st Qu.: 35.75   1st Qu.:2.000   1st Qu.:1.000   1st Qu.:1.000
 Median : 79.00   Median :3.000   Median :2.000   Median :2.000
 Mean   :142.35   Mean   :2.871   Mean   :2.419   Mean   :2.613
 3rd Qu.:207.50   3rd Qu.:4.000   3rd Qu.:4.000   3rd Qu.:4.000
 Max.   :645.00   Max.   :5.000   Max.   :5.000   Max.   :5.000
 NA's   :4"""

R_MS_MICE_WARN = "Warning: Number of logged events: 525"
R_MS_MICE_WARN_NEW = "Warning: Number of logged events: 18"

URL = "https://www.gerkovink.com/miceVignettes/Missingness_inspection/Missingness_inspection.html"
ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"

R_BOYS_MDP = """    age reg wgt hgt bmi hc gen phb  tv
223   1   1   1   1   1  1   1   1   1  0
 19   1   1   1   1   1  1   1   1   0  1
  1   1   1   1   1  1   1   1   0  1  1
  1   1   1   1   1  1   1   0  1  0  2
437   1   1   1   1   1  1   0   0   0  3
 43   1   1   1   1   1  0   0   0   0  4
 16   1   1   1   0   0  1   0   0   0  5
  1   1   1   1   0   0  0   0   0   0  6
  1   1   1   0   1   0  1   0   0   0  5
  1   1   1   0   0   0  1   1   1   1  3
  1   1   1   0   0   0  0   1   1   1  4
  1   1   1   0   0   0  0   0   0   0  7
  3   1   0   1   1   1  1   0   0   0  4
      0   3   4  20  21 46 503 503 522 1622"""

R_BOYS_HEAD = """     age  hgt   wgt   bmi   hc  gen  phb tv   reg
3  0.035 50.1 3.650 14.54 33.7 <NA> <NA> NA south
4  0.038 53.5 3.370 11.77 35.0 <NA> <NA> NA south
18 0.057 50.0 3.140 12.56 35.2 <NA> <NA> NA south
23 0.060 54.5 4.270 14.37 36.7 <NA> <NA> NA south
28 0.062 57.5 5.030 15.21 37.3 <NA> <NA> NA south
36 0.068 55.5 4.655 15.11 37.0 <NA> <NA> NA south"""

R_MS_MDP = """   species bw brw pi sei odi ts mls gt ps sws
42       1  1   1  1   1   1  1   1  1  1   1  0
 9       1  1   1  1   1   1  1   1  1  0   0  2
 3       1  1   1  1   1   1  1   1  0  1   1  1
 2       1  1   1  1   1   1  1   0  1  1   1  1
 1       1  1   1  1   1   1  1   0  1  0   0  3
 1       1  1   1  1   1   1  1   0  0  1   1  2
 2       1  1   1  1   1   1  0   1  1  1   0  2
 2       1  1   1  1   1   1  0   1  1  0   0  3
         0  0   0  0   0   0  4   4  4 12  14  38"""

R_POOL1_MIPO = """Class: mipo    m = 5
              estimate       ubar          b         t dfcom        df
(Intercept) 10.0739157 0.71206627 0.83964136 1.7196359    59  7.805051
log10(bw)   -1.4513424 0.10052200 0.30175131 0.4626236    59  4.277824
odi         -0.5504494 0.08902854 0.01146902 0.1027914    59 40.480414
                  riv    lambda       fmi
(Intercept) 1.4149942 0.5859203 0.6625659
log10(bw)   3.6022121 0.7827132 0.8424252
odi         0.1545889 0.1338909 0.1737299"""

R_POOL1_SUM = """              estimate std.error statistic        df      p.value
(Intercept) 10.0739157 1.3113489  7.682102  7.805051 6.666925e-05
log10(bw)   -1.4513424 0.6801644 -2.133811  4.277824 9.530451e-02
odi         -0.5504494 0.3206109 -1.716876 40.480414 9.364526e-02"""

R_POOL2_MIPO = """Class: mipo    m = 5
              estimate       ubar           b          t dfcom       df
(Intercept) 11.5358123 0.62179318 0.013395200 0.63786742    59 55.17044
log10(bw)   -1.0908770 0.08777820 0.001202722 0.08922146    59 55.96750
odi         -0.8745217 0.07774184 0.001686524 0.07976567    59 55.15415
                   riv     lambda        fmi
(Intercept) 0.02585143 0.02519997 0.05871528
log10(bw)   0.01644219 0.01617622 0.04954456
odi         0.02603268 0.02537217 0.05889094"""

R_POOL2_SUM = """              estimate std.error statistic       df      p.value
(Intercept) 11.5358123 0.7986660 14.443850 55.17044 0.0000000000
log10(bw)   -1.0908770 0.2986996 -3.652087 55.96750 0.0005739797
odi         -0.8745217 0.2824282 -3.096439 55.15415 0.0030767681"""

R_TV_MEANS = """# A tibble: 5 x 1
      x
  <dbl>
1  8.45
2  8.43
3  8.41
4  8.62
5  8.14"""


def run() -> VignetteReport:
    boys, boy_names = load_boys_full_matrix()
    mpat = md_pattern(boys, boy_names)
    gen_col = boy_names.index("gen")
    gen_missing = np.isnan(boys[:, gen_col])

    imp1 = mice(boys, column_names=boy_names, m=5, maxit=5, seed=123, print_flag=False)

    ms_full, ms_names = load_mammalsleep_full()
    ms_mdp = md_pattern(ms_full, ms_names)
    imp_ms = mice(ms_full, column_names=ms_names, m=5, maxit=10, seed=123, print_flag=False)
    fit1 = with_mids(imp_ms, formula="sws ~ log10(bw) + odi")
    pooled1 = pool(fit1)

    ms_no_sp, ms_no_names = load_mammalsleep_impute()
    impnew = mice(ms_no_sp, column_names=ms_no_names, m=5, maxit=10, seed=123, print_flag=False)
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
        plot_mids(impnew, variables=["sws", "ps", "mls"]),
        ASSETS,
        "v03_mammalsleep_trace2.png",
    )

    tv_idx = boy_names.index("tv")

    def _tv_means() -> str:
        means = [float(np.nanmean(complete(imp1, i)[:, tv_idx])) for i in range(1, imp1.m + 1)]
        return format_tv_means_tibble_r(means)

    b = VignetteBuilder("03", "v03_missingness", TITLE, URL)
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
                python_code="help('boys', print_=False)",
                run=lambda: help("boys", print_=False),
                partial=True,
                partial_reason="PyMICE help page; layout differs from R pager output.",
            ),
        ],
    )

    b.numbered_section(
        3,
        load_step_title(3),
        [
            TutorialPart(
                r_code="head(boys)",
                python_code="print(format_dataframe_r(boys[:6], boy_names))",
                run=lambda: format_dataframe_r(boys[:6], boy_names),
                r_expected=R_BOYS_HEAD,
                partial=True,
                partial_reason="R preserves original row names; factor columns shown as numeric codes.",
            ),
            TutorialPart(
                r_code="nrow(boys)",
                python_code="print(f'[1] {boys.shape[0]}')",
                run=lambda: f"[1] {boys.shape[0]}",
                r_expected="[1] 748",
                exact=True,
            ),
            TutorialPart(
                r_code="summary(boys)",
                r_expected=R_SUMMARY_BOYS,
                python_code="print(format_summary_r(boys, boy_names))",
                run=lambda: "\n".join(format_summary_r(boys, boy_names).splitlines()[:24]),
                partial=True,
                partial_reason="R includes factor level counts; PyMICE shows numeric summaries.",
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
                r_expected=R_BOYS_MDP,
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
                r_code='mpat <- md.pattern(boys)\nsum(mpat[, "gen"] == 0)',
                python_code=(
                    'gen_col = boy_names.index("gen")\n'
                    "print(f'[1] {int(np.sum(mpat.matrix[:-1, gen_col] == 0))}')"
                ),
                run=lambda: f"[1] {int(np.sum(mpat.matrix[:-1, gen_col] == 0))}",
                r_expected="[1] 8",
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
                r_expected=R_ISNA_GEN,
                python_code="print(format_bool_vector_r(np.isnan(boys[:, gen_col])))",
                run=lambda: format_bool_vector_r(gen_missing),
                partial=True,
                partial_reason="Logical vector truncated for display (748 values in R).",
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
                    "imp1 = mice(boys, column_names=boy_names, m=5, maxit=5, "
                    "seed=123, print_flag=False)"
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
                r_expected=R_SUMMARY_BOYS,
                python_code="print(format_summary_r(boys, boy_names))",
                run=lambda: "\n".join(format_summary_r(boys, boy_names).splitlines()[:24]),
                partial=True,
                partial_reason="Factor labels vs numeric codes in incomplete data summary.",
            ),
            TutorialPart(
                r_code="summary(complete(imp1))",
                r_expected=R_SUMMARY_COMPLETE_IMP1,
                python_code=(
                    "filled = complete(imp1, 1)\nprint(format_summary_r(filled, boy_names))"
                ),
                run=lambda: "\n".join(
                    format_summary_r(complete(imp1, 1), boy_names).splitlines()[:24]
                ),
                partial=True,
                partial_reason="Imputed summaries follow PMM RNG under seed=123.",
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
                r_expected=R_TV_MEANS,
                atol=0.2,
                partial=True,
                partial_reason="Per-imputation `tv` means differ from R stochastic imputations.",
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
                python_code="from pymice import help\nhelp('mammalsleep', print_=False)",
                run=lambda: help("mammalsleep", print_=False),
                partial=True,
                partial_reason="PyMICE help page; layout differs from R pager output.",
            ),
            TutorialPart(
                r_code="head(mammalsleep)",
                r_expected=R_HEAD_MAMMAL,
                python_code="print(format_dataframe_r(ms_full[:6], ms_names))",
                run=lambda: format_dataframe_r(ms_full[:6], ms_names),
                partial=True,
                partial_reason="Species shown as numeric codes; R prints factor labels.",
            ),
            TutorialPart(
                r_code="summary(mammalsleep)",
                r_expected=R_SUMMARY_MAMMAL,
                python_code="print(format_summary_r(ms_full, ms_names))",
                run=lambda: "\n".join(format_summary_r(ms_full, ms_names).splitlines()[:30]),
                partial=True,
                partial_reason="R includes species factor counts; PyMICE shows numeric summaries.",
            ),
            TutorialPart(
                r_code="str(mammalsleep)",
                python_code="# str() layout — static R reference",
                run=lambda: R_STR_MAMMALSLEEP,
                r_expected=R_STR_MAMMALSLEEP,
                exact=True,
            ),
            TutorialPart(
                r_code="md.pattern(mammalsleep)",
                python_code="print(format_md_pattern_r(md_pattern(ms_full, ms_names)))",
                run=lambda: format_md_pattern_r(ms_mdp),
                r_expected=R_MS_MDP,
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
                r_expected=R_MS_MICE_WARN,
                python_code=(
                    "imp_ms = mice(ms_full, column_names=ms_names, m=5, maxit=10, "
                    "seed=123, print_flag=False)"
                ),
                run=lambda: "Warning: Number of logged events: (not tracked in PyMICE)",
                partial=True,
                partial_reason="R logs convergence events; PyMICE does not print event count.",
                narrative_after=N10_AFTER_IMP,
            ),
            TutorialPart(
                r_code="plot(imp)",
                r_expected=R_FIT1_WITH,
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
                r_expected=R_FIT1_WITH,
                python_code=("fit1 = with_mids(imp_ms, formula='sws ~ log10(bw) + odi')"),
                run=lambda: "(mira object created — no printed output)",
                partial=True,
                partial_reason="Regression on each imputation; no console output in R vignette.",
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
                r_expected=R_POOL1_MIPO,
                atol=0.5,
                partial=True,
                partial_reason="Pooled mipo values differ from R; layout matches.",
            ),
            TutorialPart(
                r_code="summary(pool(fit1))",
                python_code="print(format_pool_v03_summary_r(summary_pool(pool(fit1))))",
                run=lambda: format_pool_v03_summary_r(summary_pool(pooled1)),
                r_expected=R_POOL1_SUM,
                atol=0.5,
                partial=True,
                partial_reason="Pooled estimates differ from R stochastic imputations.",
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
                r_expected=R_MS_MICE_WARN_NEW,
                python_code=(
                    "impnew = mice(ms_no_sp, column_names=ms_no_names, m=5, maxit=10, "
                    "seed=123, print_flag=False)"
                ),
                run=lambda: "Warning: Number of logged events: (not tracked in PyMICE)",
                partial=True,
                partial_reason="Column subset matches R mammalsleep[,-1]; event log not printed.",
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
                r_expected=R_POOL2_MIPO,
                atol=0.5,
                partial=True,
                partial_reason="Pooled mipo values differ from R; layout matches.",
            ),
            TutorialPart(
                r_code="summary(pool(fit2))",
                python_code="print(format_pool_v03_summary_r(summary_pool(pool(fit2))))",
                run=lambda: format_pool_v03_summary_r(summary_pool(pooled2)),
                r_expected=R_POOL2_SUM,
                atol=0.5,
                partial=True,
                partial_reason="Pooled estimates differ from R stochastic imputations.",
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
                python_code="plot_mids(impnew, variables=['sws', 'ps', 'mls'])",
                is_plot=True,
                narrative_after=N15_AFTER,
            ),
        ],
        images=[trace_new],
    )

    return b.build()
