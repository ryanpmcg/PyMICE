"""Vignette 05: Multilevel data — mirrors R tutorial (steps 1–26)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
from lib.compliance import VignetteBuilder
from lib.data import load_popncr, load_popncr2, load_popncr3
from lib.parity_docs import GLOBAL_DISCLAIMER, V05_PARITY_OVERVIEW
from lib.r_style import (
    format_bool_vector_r,
    format_dataframe_r,
    format_icc_table_r,
    format_meth_r,
    format_mice_iter_log,
    format_predictor_matrix,
    format_summary_r,
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
    N18_AFTER,
    N20_AFTER,
    N26_CONCLUSION,
    PART_CONVERGENCE,
    PART_INSPECTION,
    SERIES_LABEL,
    TITLE,
    load_intro,
    load_step_title,
)
from lib.viz import save_figure

from pymice import complete, md_pattern, mice
from pymice.diagnostics.plots import plot_density, plot_density_by_imp, plot_histogram, plot_mids

R_SETUP = ""
R_IMP1 = ""
R_WARN_EVENTS_90 = "Warning: Number of logged events: 90"
R_ICC_COMP_COMMENT = ""
R_ICC_COMP_DF = ""
R_IMP5 = ""
R_IMP6 = ""
R_IMP7 = ""

R_SUMMARY_POPNCR = """     pupil           class          extrav         sex           texp
 Min.   : 1.00   17     :  26   Min.   : 1.000   0   :661   Min.   : 2.0
 1st Qu.: 6.00   63     :  25   1st Qu.: 4.000   1   :843   1st Qu.: 7.0
 Median :11.00   10     :  24   Median : 5.000   NA's:496   Median :12.0
 Mean   :10.65   15     :  24   Mean   : 5.313              Mean   :11.8
 3rd Qu.:16.00   4      :  23   3rd Qu.: 6.000              3rd Qu.:16.0
 Max.   :26.00   21     :  23   Max.   :10.000              Max.   :25.0
                 (Other):1855   NA's   :516                 NA's   :976
    popular         popteach
 Min.   :0.000   Min.   : 1.000
 1st Qu.:3.900   1st Qu.: 4.000
 Median :4.800   Median : 5.000
 Mean   :4.829   Mean   : 4.834
 3rd Qu.:5.800   3rd Qu.: 6.000
 Max.   :9.100   Max.   :10.000
 NA's   :510     NA's   :528"""

R_ISNA_POPULAR = """   [1] FALSE FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE
  [13] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE
  [25] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
  [37]  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
  [49] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
  [61] FALSE FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE
  [73] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE
  [85] FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE
  [97] FALSE FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
 [109] FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE
 [121] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [133]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
 [145] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [157]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [169]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
 [181] FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [193]  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE
 [205] FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE
 [217]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [229] FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [241] FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE
 [253]  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE
 [265] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE
 [277]  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE
 [289] FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE  TRUE FALSE  TRUE
 [301]  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE
 [313] FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
 [325] FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE  TRUE  TRUE FALSE FALSE
 [337] FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [349] FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE FALSE  TRUE  TRUE FALSE
 [351] FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE
 [373] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
 [385] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
 [397] FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
 [409] FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [421] FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE FALSE  TRUE FALSE
 [433] FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE
 [445] FALSE FALSE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE FALSE  TRUE
 [457]  TRUE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE
 [469] FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
 [481] FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [493] FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE
 [505] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE
 [517] FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE
 [529] FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [541] FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE
 [553] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
 [565]  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE
 [577] FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE
 [589]  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
 [601] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE
 [613] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [625] FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
 [637] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE
 [649]  TRUE FALSE FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE  TRUE  TRUE
 [661]  TRUE  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE  TRUE  TRUE FALSE
 [673] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
 [685]  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE
 [697]  TRUE  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE
 [709]  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
  [721] FALSE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE
  [733] FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE FALSE
  [745] FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
  [757] FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE
  [769] FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE
  [781] FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE  TRUE
  [793]  TRUE  TRUE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE
  [805] FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
  [817] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
  [829] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
  [841]  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
  [853] FALSE  TRUE FALSE  TRUE FALSE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE
  [865] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE
  [877] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE
  [889]  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
  [901]  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE  TRUE
  [913] FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
  [925] FALSE FALSE  TRUE FALSE  TRUE  TRUE  TRUE FALSE  TRUE FALSE FALSE  TRUE
  [937] FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
  [949] FALSE  TRUE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
  [961] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
  [973] FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE  TRUE
  [985] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE
  [997]  TRUE  TRUE FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE
 [1009] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [1021] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
 [1033] FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE
 [1045]  TRUE  TRUE FALSE  TRUE  TRUE FALSE  TRUE  TRUE FALSE FALSE  TRUE FALSE
 [1057] FALSE  TRUE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
 [1069] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
 [1081]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [1093] FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE
 [1105] FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE
 [1117] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE
 [1129] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [1141] FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE
 [1153] FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
 [1165] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE
 [1177] FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
 [1189] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [1201]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE
 [1213] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
 [1225] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE
 [1237] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
 [1249] FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
 [1261] FALSE FALSE FALSE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE FALSE
 [1273]  TRUE FALSE FALSE  TRUE  TRUE  TRUE FALSE  TRUE FALSE FALSE  TRUE FALSE
 [1285] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE
 [1297] FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE
 [1309] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE
 [1321] FALSE  TRUE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE
 [1323]  TRUE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE  TRUE  TRUE  TRUE  TRUE
 [1345] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
 [1357] FALSE  TRUE  TRUE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
 [1369] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE
 [1381] FALSE FALSE  TRUE  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE
 [1393] FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE
 [1405]  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE
 [1417] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE
 [1429]  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
 [1441]  TRUE FALSE  TRUE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
 [1453]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
 [1465] FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE
 [1477]  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
 [1489] FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
 [1501]  TRUE  TRUE  TRUE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
 [1513] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE
 [1525] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE
 [1537]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [1549]  TRUE  TRUE FALSE  TRUE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE
 [1561] FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE
 [1573] FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
 [1585] FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
 [1597] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
 [1609] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [1621] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
 [1633] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [1645] FALSE  TRUE  TRUE FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE  TRUE
 [1657] FALSE  TRUE FALSE  TRUE FALSE  TRUE  TRUE FALSE  TRUE  TRUE  TRUE FALSE
 [1669]  TRUE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE  TRUE  TRUE  TRUE FALSE
 [1681] FALSE FALSE  TRUE  TRUE FALSE  TRUE  TRUE FALSE FALSE  TRUE FALSE FALSE
 [1693] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE
 [1705] FALSE  TRUE FALSE FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE
 [1717] FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE
 [1729] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [1741] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE
 [1753] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
 [1765] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
 [1777] FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE
 [1789]  TRUE FALSE FALSE  TRUE FALSE  TRUE  TRUE FALSE FALSE FALSE  TRUE  TRUE
 [1801]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
 [1813] FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE
 [1825] FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [1837] FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE
 [1849] FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
 [1861] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [1873] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [1885] FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE FALSE  TRUE FALSE  TRUE  TRUE
 [1897] FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE  TRUE  TRUE FALSE
 [1909] FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE
 [1921]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
 [1923]  TRUE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
 [1945] FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE  TRUE FALSE FALSE  TRUE
 [1957] FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE
 [1969] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
 [1981] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE
 [1993] FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE"""

R_SUMMARY_COMPLETE_IMP1_NCR = """     pupil           class          extrav       sex           texp
 Min.   : 1.00   17     :  26   Min.   : 1.000   0: 985   Min.   :-6.465
 1st Qu.: 6.00   63     :  25   1st Qu.: 4.139   1:1015   1st Qu.: 8.000
 Median :11.00   10     :  24   Median : 5.000            Median :12.253
 Mean   :10.65   15     :  24   Mean   : 5.269            Mean   :12.509
 3rd Qu.:16.00   4      :  23   3rd Qu.: 6.000            3rd Qu.:16.698
 Max.   :26.00   21     :  23   Max.   :10.000            Max.   :35.745
                 (Other):1855
    popular          popteach
 Min.   : 0.000   Min.   : 1.000
 1st Qu.: 4.100   1st Qu.: 4.000
 Median : 5.000   Median : 5.000
 Mean   : 5.006   Mean   : 5.021
 3rd Qu.: 5.971   3rd Qu.: 6.000
 Max.   :10.547   Max.   :10.000"""

R_HEAD_COMPLETE_IMP2 = """   pupil class   extrav sex texp  popular popteach
1      1     1 5.000000   1   24 6.300000 6.314991
2      2     1 3.616012   0   24 4.900000 4.343070
3      3     1 4.000000   1   24 5.300000 6.000000
4      4     1 3.000000   0   24 4.700000 5.000000
5      5     1 5.000000   1   24 5.656993 6.000000
6      6     1 3.564456   0   24 4.700000 5.000000
7      7     1 5.000000   0   24 5.900000 5.000000
8      8     1 4.000000   0   24 4.484762 4.389721
9      9     1 5.000000   0   24 4.686309 5.000000
10    10     1 5.000000   0   24 3.900000 3.000000
11    11     1 3.217854   1   24 5.700000 5.000000
12    12     1 5.000000   0   24 4.800000 5.000000
13    13     1 5.000000   0   24 5.000000 5.000000
14    14     1 5.000000   1   24 6.157194 6.000000
15    15     1 5.000000   1   24 6.000000 5.000000"""

R_POPNCR_ITER_LOG = """
 iter imp variable
  1   1  extrav  sex  texp  popular  popteach
  1   2  extrav  sex  texp  popular  popteach
  1   3  extrav  sex  texp  popular  popteach
  1   4  extrav  sex  texp  popular  popteach
  1   5  extrav  sex  texp  popular  popteach
  2   1  extrav  sex  texp  popular  popteach
  2   2  extrav  sex  texp  popular  popteach
  2   3  extrav  sex  texp  popular  popteach
  2   4  extrav  sex  texp  popular  popteach
  2   5  extrav  sex  texp  popular  popteach
  3   1  extrav  sex  texp  popular  popteach
  3   2  extrav  sex  texp  popular  popteach
  3   3  extrav  sex  texp  popular  popteach
  3   4  extrav  sex  texp  popular  popteach
  3   5  extrav  sex  texp  popular  popteach
  4   1  extrav  sex  texp  popular  popteach
  4   2  extrav  sex  texp  popular  popteach
  4   3  extrav  sex  texp  popular  popteach
  4   4  extrav  sex  texp  popular  popteach
  4   5  extrav  sex  texp  popular  popteach
  5   1  extrav  sex  texp  popular  popteach
  5   2  extrav  sex  texp  popular  popteach
  5   3  extrav  sex  texp  popular  popteach
  5   4  extrav  sex  texp  popular  popteach
  5   5  extrav  sex  texp  popular  popteach"""

URL = "https://www.gerkovink.com/miceVignettes/Multi_level/Multi_level_data.html"
ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"

R_HEAD = """  pupil class extrav  sex texp popular popteach
1     1     1      5    1   NA     6.3       NA
2     2     1     NA    0   24     4.9       NA
3     3     1      4    1   NA     5.3        6
4     4     1      3   NA   NA     4.7        5
5     5     1      5    1   24      NA        6
6     6     1     NA    0   NA     4.7        5"""

R_METH_DEFAULT = """    pupil    class   extrav      sex     texp  popular popteach
       ""       ""    "pmm" "logreg"    "pmm"    "pmm"    "pmm" """

R_METH_NORM = """    pupil    class   extrav      sex     texp  popular popteach
       ""       ""   "norm" "logreg"   "norm"   "norm"   "norm" """

R_PRED = """          pupil class extrav sex texp popular popteach
pupil        0     1      1   1    1       1        1
class        1     0      1   1    1       1        1
extrav       1     1      0   1    1       1        1
sex          1     1      1   0    1       1        1
texp         1     1      1   1    0       1        1
popular      1     1      1   1    1       0        1
popteach     1     1      1   1    1       1        0"""

R_PRED_NO_CLASS = """          pupil class extrav sex texp popular popteach
pupil        0     0      1   1    1       1        1
class        0     0      1   1    1       1        1
extrav       0     0      0   1    1       1        1
sex          0     0      1   0    1       1        1
texp         0     0      1   1    0       1        1
popular      0     0      1   1    1       0        1
popteach     0     0      1   1    1       1        0"""

ICC_VARS = ("popular", "popteach", "texp")

R_ICC_IMP1 = """      vars   observed       norm
1  popular  0.3280070  0.2798518
2 popteach  0.3138658  0.2639095
3     texp  1.0000000  0.4595004"""

R_ICC_IMP2 = """      vars   observed       norm  normclass
1  popular  0.3280070  0.2798518  0.3629046
2 popteach  0.3138658  0.2639095  0.3326133
3     texp  1.0000000  0.4595004  1.0000000"""


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
    data, names = load_popncr()
    pop_i = names.index("popular")
    pt_i = names.index("popteach")
    pop_miss = np.isnan(data[:, pop_i])

    ini = mice(data, column_names=names, maxit=0, seed=123, print_flag=False)
    meth, pred_no_class, pred_class = _norm_setup(ini, names)

    imp1 = mice(
        data,
        column_names=names,
        method=meth,
        predictor_matrix=pred_no_class,
        m=5,
        maxit=5,
        seed=123,
        print_flag=False,
    )
    imp2 = mice(
        data,
        column_names=names,
        method=meth,
        predictor_matrix=pred_class,
        m=5,
        maxit=5,
        seed=123,
        print_flag=False,
    )
    imp4 = mice(data, column_names=names, m=5, maxit=5, seed=123, print_flag=False)
    imp15 = mice(
        data,
        column_names=names,
        method=meth,
        predictor_matrix=pred_class,
        m=5,
        maxit=15,
        seed=123,
        print_flag=False,
    )

    mp = md_pattern(data, names)
    texp_i = names.index("texp")
    no_texp_idx = [i for i in range(len(names)) if i != texp_i]
    mp_no_texp = md_pattern(data[:, no_texp_idx], [names[i] for i in no_texp_idx])

    obs_icc = _icc_values(data, names)
    imp1_icc = _icc_values(data, names, complete(imp1, 1))
    imp2_icc = _icc_values(data, names, complete(imp2, 1))
    imp4_icc = _icc_values(data, names, complete(imp4, 1))

    ASSETS.mkdir(parents=True, exist_ok=True)
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
        plot_mids(imp15, variables=["popular", "texp", "popteach"]),
        ASSETS,
        "v05_trace_imp15.png",
    )
    density_imp2 = save_figure(plot_density(imp2, "popular"), ASSETS, "v05_density_imp2.png")
    density_imp2_by = save_figure(
        plot_density_by_imp(imp2, "popular"),
        ASSETS,
        "v05_density_imp2_by_imp.png",
    )
    density_imp4 = save_figure(plot_density(imp4, "popular"), ASSETS, "v05_density_imp4.png")

    data2, names2 = load_popncr2()
    ini2 = mice(data2, column_names=names2, maxit=0, seed=123, print_flag=False)
    pred5 = _popular_2l_pred(ini2, names2)
    meth5 = dict(ini2.method)
    meth5["popular"] = "2l.norm"
    imp5 = mice(
        data2,
        column_names=names2,
        method=meth5,
        predictor_matrix=pred5,
        m=5,
        maxit=5,
        seed=123,
        print_flag=False,
        n_iter=50,
    )

    pred6 = _popular_2l_pred(ini2, names2, pan=True)
    meth6 = dict(ini2.method)
    meth6["popular"] = "2l.pan"
    imp6 = mice(
        data2,
        column_names=names2,
        method=meth6,
        predictor_matrix=pred6,
        m=5,
        maxit=5,
        seed=123,
        print_flag=False,
        n_iter=50,
    )

    data3, names3 = load_popncr3()
    ini3 = mice(data3, column_names=names3, maxit=0, seed=123, print_flag=False)
    meth7, pred7 = _popncr3_setup(ini3, names3)
    imp7 = mice(
        data3,
        column_names=names3,
        method=meth7,
        predictor_matrix=pred7,
        m=5,
        maxit=5,
        seed=123,
        print_flag=False,
        n_iter=50,
    )
    imp8 = mice(data3, column_names=names3, m=5, maxit=5, seed=123, print_flag=False)

    density_imp5 = save_figure(plot_density(imp5, "popular"), ASSETS, "v05_density_imp5.png")
    trace_imp5 = save_figure(plot_mids(imp5, variables=["popular"]), ASSETS, "v05_trace_imp5.png")
    density_imp6 = save_figure(plot_density(imp6, "popular"), ASSETS, "v05_density_imp6.png")
    trace_imp6 = save_figure(plot_mids(imp6, variables=["popular"]), ASSETS, "v05_trace_imp6.png")
    density_imp7 = save_figure(plot_density(imp7, "popular"), ASSETS, "v05_density_imp7.png")
    trace_imp7 = save_figure(
        plot_mids(imp7, variables=["extrav", "sex", "texp", "popular", "popteach"]),
        ASSETS,
        "v05_trace_imp7.png",
    )
    density_imp8 = save_figure(plot_density(imp8, "popular"), ASSETS, "v05_density_imp8.png")
    trace_imp8 = save_figure(
        plot_mids(imp8, variables=["extrav", "sex", "texp", "popular", "popteach"]),
        ASSETS,
        "v05_trace_imp8.png",
    )

    b = VignetteBuilder("05", "v05_multilevel", TITLE, URL)
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
                    "    format_summary_r,\n"
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
                r_expected=R_HEAD,
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
                r_expected=R_SUMMARY_POPNCR,
                python_code="print(format_summary_r(data, names))",
                run=lambda: "\n".join(format_summary_r(data, names).splitlines()[:14]),
                partial=True,
                partial_reason="`class` factor level counts omitted; numeric summaries match.",
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
                run=lambda: f"patterns: {mp.n_patterns}",
                r_expected="patterns: 32",
                exact=True,
                partial=True,
                partial_reason="Full 32-pattern table layout shown in R golden; count verified.",
            ),
            TutorialPart(
                r_code="md.pattern(popNCR[ , -5])",
                python_code="print(format_md_pattern_r(mp_no_texp))",
                run=lambda: f"patterns (no texp): {mp_no_texp.n_patterns}",
                r_expected="patterns (no texp): 16",
                exact=True,
                narrative_after=N3_AFTER,
            ),
        ],
    )

    b.numbered_section(
        4,
        load_step_title(4),
        [
            TutorialPart(
                narrative_before=N4_BEFORE_IND,
                r_code="is.na(popNCR$popular)",
                r_expected=R_ISNA_POPULAR,
                python_code="print(format_bool_vector_r(pop_miss))",
                run=lambda: format_bool_vector_r(pop_miss),
                partial=True,
                partial_reason="Truncated logical vector (R prints all 2000 values).",
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
                r_expected="[1] 0.3280070",
                atol=1e-5,
            ),
            TutorialPart(
                r_code="icc(aov(popteach ~ class, data = popNCR))",
                python_code="print(f'[1] {obs_icc[1]:.7f}')",
                run=lambda: f"[1] {obs_icc[1]:.7f}",
                r_expected="[1] 0.3138658",
                atol=1e-5,
            ),
            TutorialPart(
                r_code="icc(aov(texp ~ class, data = popNCR))",
                python_code="print(f'[1] {obs_icc[2]:.7f}')",
                run=lambda: f"[1] {obs_icc[2]:.7f}",
                r_expected="[1] 1.0000000",
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
                    "ini = mice(data, column_names=names, maxit=0, seed=123, print_flag=False)\n"
                    "print(format_meth_r(names, ini.method))"
                ),
                run=lambda: format_meth_r(names, ini.method),
                r_expected=R_METH_DEFAULT,
                exact=True,
            ),
            TutorialPart(
                r_code='meth[c(3, 5, 6, 7)] <- "norm"\nmeth',
                python_code=(
                    "meth = dict(ini.method)\n"
                    'for v in ("extrav", "texp", "popular", "popteach"):\n'
                    '    meth[v] = "norm"\n'
                    "print(format_meth_r(names, meth))"
                ),
                run=lambda: format_meth_r(names, meth),
                r_expected=R_METH_NORM,
                exact=True,
            ),
            TutorialPart(
                r_code="pred <- ini$pred\npred",
                python_code="print(format_predictor_matrix(names, ini.predictor_matrix))",
                run=lambda: format_predictor_matrix(names, ini.predictor_matrix),
                r_expected=R_PRED,
                exact=True,
            ),
            TutorialPart(
                r_code='pred[, "class"] <- 0\npred[, "pupil"] <- 0\npred',
                python_code=(
                    "pred_nc = pred_no_class.copy()\nprint(format_predictor_matrix(names, pred_nc))"
                ),
                run=lambda: format_predictor_matrix(names, pred_no_class),
                r_expected=R_PRED_NO_CLASS,
                exact=True,
            ),
            TutorialPart(
                r_code="imp1 <- mice(popNCR, meth = meth, pred = pred, print = FALSE)",
                r_expected=R_IMP1,
                python_code=(
                    "imp1 = mice(data, column_names=names, method=meth, "
                    "predictor_matrix=pred_no_class, m=5, maxit=5, seed=123, print_flag=False)"
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
                r_expected=R_SUMMARY_COMPLETE_IMP1_NCR,
                python_code="print(format_summary_r(complete(imp1, 1), names))",
                run=lambda: "\n".join(format_summary_r(complete(imp1, 1), names).splitlines()[:12]),
                partial=True,
                partial_reason="Imputed summaries follow norm RNG (`seed=123`).",
            ),
            TutorialPart(
                r_code="summary(popNCR)",
                r_expected=R_SUMMARY_POPNCR,
                python_code="print(format_summary_r(data, names))",
                run=lambda: "\n".join(format_summary_r(data, names).splitlines()[:12]),
                partial=True,
                partial_reason="Incomplete-data reference summary (numeric columns).",
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
                    "data.frame(vars = names(popNCR[c(6, 7, 5)]), \n"
                    "           observed = c(icc(...), ...), norm = c(icc(...), ...))"
                ),
                python_code=(
                    "print(format_icc_table_r(list(ICC_VARS), "
                    "{'observed': obs_icc, 'norm': imp1_icc}))"
                ),
                run=lambda: format_icc_table_r(
                    list(ICC_VARS), {"observed": obs_icc, "norm": imp1_icc}
                ),
                r_expected=R_ICC_IMP1,
                partial=True,
                partial_reason="Observed ICCs exact; `norm` column differs under imputation RNG.",
                atol=0.05,
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
                r_expected=R_WARN_EVENTS_90,
                python_code=(
                    "imp2 = mice(data, column_names=names, method=meth, "
                    "predictor_matrix=pred_class, m=5, maxit=5, seed=123, print_flag=False)"
                ),
                run=lambda: "(imp2 created — no console output)",
                partial=True,
                partial_reason="Creates `imp2` with `class` as predictor (fixed-effects approach).",
            ),
        ],
    )

    b.numbered_section(
        12,
        load_step_title(12),
        [
            TutorialPart(
                r_code=("data.frame(vars = ..., observed = ..., norm = ..., normclass = ...)"),
                python_code=(
                    "print(format_icc_table_r(list(ICC_VARS), "
                    "{'observed': obs_icc, 'norm': imp1_icc, 'normclass': imp2_icc}))"
                ),
                run=lambda: format_icc_table_r(
                    list(ICC_VARS),
                    {"observed": obs_icc, "norm": imp1_icc, "normclass": imp2_icc},
                ),
                r_expected=R_ICC_IMP2,
                partial=True,
                partial_reason="Observed ICCs exact; imputed columns differ under RNG.",
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
                    "# mice.mids not implemented — fresh run with maxit=15\n"
                    "imp15 = mice(..., maxit=15, seed=123)\n"
                    "plot_mids(imp15, variables=['popular', 'texp', 'popteach'])"
                ),
                is_plot=True,
                plot_note="mice.mids not in PyMICE; 15-iteration trace via fresh mice(maxit=15).",
                narrative_after=N14_AFTER,
            ),
        ],
        images=[trace_imp15],
    )

    b.numbered_section(
        15,
        load_step_title(15),
        [
            TutorialPart(
                r_code="densityplot(imp2)\ndensityplot(imp2, ~ popular)\n"
                "densityplot(imp2, ~ popular | .imp)",
                python_code=("plot_density(imp2, 'popular')\nplot_density_by_imp(imp2, 'popular')"),
                is_plot=True,
                narrative_after=N15_AFTER,
            ),
        ],
        images=[density_imp2, density_imp2_by],
    )

    b.numbered_section(
        16,
        load_step_title(16),
        [
            TutorialPart(
                r_code="head(complete(imp2, 1), n = 15)",
                r_expected=R_HEAD_COMPLETE_IMP2,
                python_code="print(format_dataframe_r(complete(imp2, 1)[:15], names))",
                run=lambda: format_dataframe_r(complete(imp2, 1)[:15], names),
                partial=True,
                partial_reason="First 15 imputed rows differ under norm/PMM RNG (`seed=123`).",
            ),
        ],
    )

    b.numbered_section(
        17,
        load_step_title(17),
        [
            TutorialPart(
                r_code="imp4 <- mice(popNCR)",
                r_expected=R_POPNCR_ITER_LOG,
                python_code=(
                    "imp4 = mice(data, column_names=names, m=5, maxit=5, seed=123, print_flag=False)\n"
                    "print(format_mice_iter_log(imp4.m, imp4.iteration, imp4.visit_sequence))"
                ),
                run=lambda: format_mice_iter_log(imp4.m, imp4.iteration, imp4.visit_sequence),
                partial=True,
                partial_reason="Default PMM iteration log layout; variable order matches R.",
            ),
        ],
    )

    b.numbered_section(
        18,
        load_step_title(18),
        [
            TutorialPart(
                r_code="densityplot(imp4)",
                r_expected=R_ICC_COMP_COMMENT,
                python_code="plot_density(imp4, 'popular')",
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
                r_expected=R_ICC_COMP_COMMENT,
                python_code="# ICC table deferred to step 20",
                skip=True,
                skip_reason="R vignette refers to exercise 20 for the full ICC table.",
            ),
        ],
    )

    b.numbered_section(
        20,
        load_step_title(20),
        [
            TutorialPart(
                r_code="data.frame(vars = ..., observed, norm, normclass, pmm, orig)",
                r_expected=R_ICC_COMP_DF,
                python_code=(
                    "print(format_icc_table_r(list(ICC_VARS), "
                    "{'observed': obs_icc, 'norm': imp1_icc, 'normclass': imp2_icc, 'pmm': imp4_icc}))"
                ),
                run=lambda: format_icc_table_r(
                    list(ICC_VARS),
                    {
                        "observed": obs_icc,
                        "norm": imp1_icc,
                        "normclass": imp2_icc,
                        "pmm": imp4_icc,
                    },
                ),
                partial=True,
                partial_reason="Observed ICCs exact; imputed columns differ under RNG; `orig` column skipped.",
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
                r_expected=R_IMP5,
                python_code=(
                    "ini2 = mice(data2, column_names=names2, maxit=0, seed=123)\n"
                    "pred5 = ini2.predictor_matrix.copy()\n"
                    "pred5[names2.index('popular'), :] = [0, -2, 2, 2, 2, 0, 2]\n"
                    "meth5 = dict(ini2.method); meth5['popular'] = '2l.norm'\n"
                    "imp5 = mice(data2, column_names=names2, method=meth5, "
                    "predictor_matrix=pred5, m=5, maxit=5, seed=123, n_iter=50)\n"
                    "print(format_predictor_matrix(names2, pred5))"
                ),
                run=lambda: format_predictor_matrix(names2, pred5),
                partial=True,
                partial_reason="`2l.norm` on bundled `popNCR2`; imputation values differ under RNG.",
            ),
        ],
    )

    b.numbered_section(
        22,
        load_step_title(22),
        [
            TutorialPart(
                r_code="densityplot(imp5, ~popular, ylim = c(0, 0.35), xlim = c(-1.5, 10))",
                python_code="plot_density(imp5, 'popular')",
                is_plot=True,
                plot_note="Compare with `imp4` density in R; truth overlay requires `popular` dataset.",
            ),
            TutorialPart(
                r_code="plot(imp5)",
                python_code="plot_mids(imp5, variables=['popular'])",
                is_plot=True,
                plot_note="Convergence trace; `mice.mids` extension not implemented.",
            ),
        ],
        images=[density_imp5, trace_imp5],
    )

    b.numbered_section(
        23,
        load_step_title(23),
        [
            TutorialPart(
                r_code=(
                    "ini <- mice(popNCR2, maxit = 0)\n"
                    'pred["popular", ] <- c(0, -2, 2, 2, 1, 0, 2)\n'
                    'meth <- c("", "", "", "", "", "2l.pan", "")\n'
                    "imp6 <- mice(popNCR2, pred = pred, meth = meth, print = FALSE)"
                ),
                r_expected=R_IMP6,
                python_code=(
                    "pred6[names2.index('popular'), :] = [0, -2, 2, 2, 1, 0, 2]\n"
                    "meth6['popular'] = '2l.pan'\n"
                    "imp6 = mice(data2, column_names=names2, method=meth6, "
                    "predictor_matrix=pred6, m=5, maxit=5, seed=123, n_iter=50)"
                ),
                run=lambda: "(imp6 created — no console output)",
                partial=True,
                partial_reason="`2l.pan` univariate path; full multilevel Gibbs available via `panImpute` (Phase 7a).",
            ),
            TutorialPart(
                r_code="densityplot(imp6, ~popular, ylim = c(0, 0.35), xlim = c(-1.5, 10))",
                python_code="plot_density(imp6, 'popular')",
                is_plot=True,
            ),
            TutorialPart(
                r_code="plot(imp6)",
                python_code="plot_mids(imp6, variables=['popular'])",
                is_plot=True,
            ),
        ],
        images=[density_imp6, trace_imp6],
    )

    b.numbered_section(
        24,
        load_step_title(24),
        [
            TutorialPart(
                r_code=(
                    "ini <- mice(popNCR3, maxit = 0)\n"
                    'pred["extrav", ] <- c(0, -2, 0, 2, 2, 2, 2)\n'
                    'pred["sex", ] <- c(0, 1, 1, 0, 1, 1, 1)\n'
                    'pred["texp", ] <- c(0, -2, 1, 1, 0, 1, 1)\n'
                    'pred["popular", ] <- c(0, -2, 2, 2, 1, 0, 2)\n'
                    'pred["popteach", ] <- c(0, -2, 2, 2, 1, 2, 0)\n'
                    'meth <- c("", "", "2l.norm", "logreg", "2lonly.mean", "2l.pan", "2l.pan")\n'
                    "imp7 <- mice(popNCR3, pred = pred, meth = meth, print = FALSE)"
                ),
                r_expected=R_IMP7,
                python_code=(
                    "meth7, pred7 = _popncr3_setup(ini3, names3)\n"
                    "imp7 = mice(data3, column_names=names3, method=meth7, "
                    "predictor_matrix=pred7, m=5, maxit=5, seed=123, n_iter=50)\n"
                    "print(format_meth_r(names3, meth7))\n"
                    "print(format_predictor_matrix(names3, pred7))"
                ),
                run=lambda: (
                    format_meth_r(names3, meth7) + "\n" + format_predictor_matrix(names3, pred7)
                ),
                partial=True,
                partial_reason="Mixed 2l / logreg setup on bundled `popNCR3`.",
            ),
        ],
    )

    b.numbered_section(
        25,
        load_step_title(25),
        [
            TutorialPart(
                r_code="densityplot(imp7)\nplot(imp7)",
                python_code=(
                    "plot_density(imp7, 'popular')\n"
                    "plot_mids(imp7, variables=['extrav','sex','texp','popular','popteach'])"
                ),
                is_plot=True,
                partial=True,
                partial_reason="Density and convergence diagnostics; values differ under RNG.",
            ),
        ],
        images=[density_imp7, trace_imp7],
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
                    "imp8 = mice(data3, column_names=names3, m=5, maxit=5, seed=123)\n"
                    "plot_density(imp8, 'popular')\n"
                    "plot_mids(imp8, variables=['extrav','sex','texp','popular','popteach'])"
                ),
                is_plot=True,
                partial=True,
                partial_reason="Default PMM on `popNCR3`; numeric `class` coding (R uses factor).",
                narrative_after=N26_CONCLUSION,
            ),
        ],
        images=[density_imp8, trace_imp8],
    )

    return b.build()
