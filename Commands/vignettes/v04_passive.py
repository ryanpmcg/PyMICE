"""Vignette 04: Passive imputation and post-processing — mirrors R tutorial (steps 1–9)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
from lib.compliance import VignetteBuilder
from lib.data import load_boys_impute, load_mammalsleep_impute
from lib.parity_docs import GLOBAL_DISCLAIMER, V04_PARITY_OVERVIEW
from lib.r_style import format_meth_r, format_predictor_matrix, format_table_r
from lib.report import VignetteReport
from lib.tutorial_section import TutorialPart
from lib.v04_narrative import (
    AUTHORS,
    N1_AFTER,
    N1_PASSIVE,
    N2_AFTER,
    N3_AFTER,
    N3_POST,
    N4_AFTER,
    N5_AFTER_DENSITY,
    N5_AFTER_HIST,
    N5_AFTER_NORM,
    N5_BEFORE_PMM,
    N6_AFTER,
    N7_AFTER,
    N8_BEFORE_PLOT,
    N8_BEFORE_XY,
    N9_AFTER_OK,
    N9_AFTER_PRED,
    N9_BEFORE_PRED,
    N9_BEFORE_TRACE,
    N9_BEFORE_XY,
    N9_CONCLUSION,
    N9_FUN,
    N9_FUN_AFTER,
    PART_POST,
    SERIES_LABEL,
    TITLE,
    load_intro,
    load_step_title,
)
from lib.viz import save_figure

from pymice import complete, mice, post_squeeze
from pymice.diagnostics.plots import plot_density, plot_mids, plot_xy_imputed

R_SETUP = ""
R_MICE_BOYS_PASSIVE = ""
R_MICE_PMM = ""
R_MICE_BOYS_BMI = ""
R_MICE_BOYS_METH = ""
R_MICE_PATH = ""

R_TABLE_TV = """
               1 1.21710148525462 1.43588483352455 1.51201882679116
             323                1                1                1
1.53292756925877 1.53884163903632 1.58285408167725 1.80802667422845
               1                1                1                1
               2 2.07663165624588 2.24979678211323 2.92335718014784
              26                1                1                1
2.94117422338134 2.95084234692005                3 3.02364296734824
               1                1               19                1
3.53970347137679 3.57972881016042 3.74672076785238 3.96039115719309
               1                1                1                1
               4 4.04754711531009 4.08248223904697 4.14754362271122
              17                1                1                1
4.17913738746458  4.5108993044032 4.57883711875945 4.72773944856595
               1                1                1                1
4.78039105160729 4.87498648012577 4.95790683812151                5
               1                1                1                5
5.22626498342572 5.27699780349692 5.29699542293051  5.5135973716855
               1                1                1                1
5.58961218020009 5.69794944880459                6 6.25631547711316
               1                1               10                1
6.35152222227269 6.50171770177514 7.15463206998544 7.41565552751217
               1                1                1                1
7.91305727094718 7.93871120477867                8 8.05174592128119
               1                1               13                1
8.05700045665079 8.16362288564921 8.21549432374612 8.49997598070039
               1                1                1                1
8.51370505398192 8.58764399352692 8.61845893470197 8.97364475446134
               1                1                1                1
               9 9.00919768391507 9.63183636229161 9.63562902483335
               1                1                1                1
9.76095833349053 9.84465985091274               10 10.2674945703833
               1                1               16                1
10.4662560634783 10.5268192284329 10.5687382671324 10.6082021769037
               1                1                1                1
10.6737703082101 10.8772940701329 10.8854812337215  10.930532331179
               1                1                1                1
11.0093322524732 11.1652748123109 11.2642535206875 11.5290193322052
               1                1                1                1
11.7584784239471 11.7965517201956 11.8064326042326               12
               1                1                1               15
12.1696703772424  12.592892417515  12.618204518511 12.6689878607267
               1                1                1                1
12.7081972517136 12.8979961443309               13 13.0240980425785
               1                1                1                1
13.0587048153365  13.106348108398 13.5405375517151 13.9431160205217
               1                1                1                1
              14 14.2482185768873 14.2798608007013 14.3315252653246
               1                1                1                1
14.4076303004689 14.4338076497289 14.5138128344765 14.6788476362263
               1                1                1                1
14.6824007199852 14.7441518164776 14.8078250873427 14.9525753157757
               1                1                1                1
14.9981738657718               15 15.1258748162893 15.1835169459907
               1               27                1                1
15.4911886491463 15.5120235066289 15.6264815503803 15.6348463939284
               1                1                1                1
15.6933134568447 15.7497016188987 15.7977063752737 15.8513524150625
               1                1                1                1
15.9198411082574 15.9284148402579               16  16.340697942133
               1                1                1                1
16.3716211968936 16.4317068195426 16.4699630810462 16.5178617262188
               1                1                1                1
16.6654847715227 16.6721133690251 16.6871350554192 16.7050893382433
               1                1                1                1
16.7500877350959  16.919505854755 16.9696935240149               17
               1                1                1                1
17.0607955750451  17.061123780778 17.0975117585518 17.1863794919946
               1                1                1                1
17.2885587826642 17.3213750660243 17.3288063082604 17.3371972081781
               1                1                1                1
17.4139221505318 17.5083623700701  17.525693552751 17.5536295065084
               1                1                1                1
17.7355682743341 17.7543354628357 17.7767055311222 17.7892576850834
               1                1                1                1
17.8020025078871 17.9058272130569 17.9861341293521               18
               1                1                1                1
18.0089953938541 18.0125066085225 18.0780752065915 18.0894548325433
               1                1                1                1
18.1085713536776 18.4853383062642 18.4943336555561 18.6076606087712
               1                1                1                1
18.6213898628289 18.7328605098401 18.8458099353893 18.8627827329173
               1                1                1                1
19.0764930131297 19.2910290679375 19.3288860993901 19.4126039248187
               1                1                1                1
19.6064318553331  19.653890171068 19.6670241312546 19.8448125657382
               1                1                1                1
19.8516466793385               20  20.006279627252 20.1685051396209
               1               38                1                1
20.2483453303049 20.4090716225676 20.5489240439564 20.7075019374611
               1                1                1                1
 20.848944671593 20.8504396969632 20.9256973033623 21.2111117512718
               1                1                1                1
21.2988437259828 21.4887083820786 21.6632008465181 21.8584346902023
               1                1                1                1
21.9017081211805 22.0705004778976 22.3764963365167 22.4619460041735
               1                1                1                1
22.6563991359074 22.9207287921778 22.9263656773065 23.0539049074043
               1                1                1                1
23.0557994938662 23.4243509549263  23.554099918438 23.7245812810879
               1                1                1                1
23.7401686860153 23.8808526223058 23.9241225232408 24.4052538064194
               1                1                1                1
24.4395463953961 24.6699887395728               25
               1                1               44"""

URL = "https://www.gerkovink.com/miceVignettes/Passive_Post_processing/Passive_imputation_post_processing.html"
ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"

R_METH_MS = """   bw   brw   sws    ps    ts   mls    gt    pi   sei   odi
   ""    "" "pmm" "pmm" "pmm" "pmm" "pmm"    ""    ""    \"\""""

R_PRED_MS = """     bw brw sws ps ts mls gt pi sei odi
 bw   0   1   1  1  1   1  1  1   1   1
brw   1   0   1  1  1   1  1  1   1   1
sws   1   1   0  1  1   1  1  1   1   1
 ps   1   1   1  0  1   1  1  1   1   1
 ts   1   1   1  1  0   1  1  1   1   1
mls   1   1   1  1  1   0  1  1   1   1
 gt   1   1   1  1  1   1  0  1   1   1
 pi   1   1   1  1  1   1  1  0   1   1
sei   1   1   1  1  1   1  1  1   0   1
odi   1   1   1  1  1   1  1  1   1   0"""

R_PRED_MS_MOD = """     bw brw sws ps ts mls gt pi sei odi
 bw   0   1   1  1  1   1  1  1   1   1
brw   1   0   1  1  1   1  1  1   1   1
sws   1   1   0  1  0   1  1  1   1   1
 ps   1   1   1  0  0   1  1  1   1   1
 ts   1   1   1  1  0   1  1  1   1   1
mls   1   1   1  1  1   0  1  1   1   1
 gt   1   1   1  1  1   1  0  1   1   1
 pi   1   1   1  1  1   1  1  0   1   1
sei   1   1   1  1  1   1  1  1   0   1
odi   1   1   1  1  1   1  1  1   1   0"""

R_PRED_BOYS = """    age hgt wgt bmi hc gen phb tv reg
age   0   1   1   1  1   1   1  1   1
hgt   1   0   1   1  1   1   1  1   1
wgt   1   1   0   1  1   1   1  1   1
bmi   1   1   1   0  1   1   1  1   1
hc    1   1   1   1  0   1   1  1   1
gen   1   1   1   1  1   0   1  1   1
phb   1   1   1   1  1   1   0  1   1
tv    1   1   1   1  1   1   1  0   1
reg   1   1   1   1  1   1   1  1   0"""

R_PRED_BOYS_MOD = """    age hgt wgt bmi hc gen phb tv reg
age   0   1   1   1  1   1   1  1   1
hgt   1   0   1   0  1   1   1  1   1
wgt   1   1   0   0  1   1   1  1   1
bmi   1   1   1   0  1   1   1  1   1
hc    1   1   1   1  0   1   1  1   1
gen   1   1   1   1  1   0   1  1   1
phb   1   1   1   1  1   1   0  1   1
tv    1   1   1   1  1   1   1  0   1
reg   1   1   1   1  1   1   1  1   0"""

R_TABLE_PMM = """  1   2   3   4   5   6   8   9  10  12  13  14  15  16  17  18  20  25
 73 219  99  29   6  16  26   1  37  29   3   5  47   1   1   4  88  64"""

R_PATH_ITER = """
 iter imp variable
  1   1  hgt  wgt  bmi  hc  gen  phb  tv  reg
  1   2  hgt  wgt  bmi  hc  gen  phb  tv  reg
  1   3  hgt  wgt  bmi  hc  gen  phb  tv  reg
  1   4  hgt  wgt  bmi  hc  gen  phb  tv  reg
  1   5  hgt  wgt  bmi  hc  gen  phb  tv  reg
  2   1  hgt  wgt  bmi  hc  gen  phb  tv  reg
  2   2  hgt  wgt  bmi  hc  gen  phb  tv  reg
  2   3  hgt  wgt  bmi  hc  gen  phb  tv  reg
  2   4  hgt  wgt  bmi  hc  gen  phb  tv  reg
  2   5  hgt  wgt  bmi  hc  gen  phb  tv  reg
  3   1  hgt  wgt  bmi  hc  gen  phb  tv  reg
  3   2  hgt  wgt  bmi  hc  gen  phb  tv  reg
  3   3  hgt  wgt  bmi  hc  gen  phb  tv  reg
  3   4  hgt  wgt  bmi  hc  gen  phb  tv  reg
  3   5  hgt  wgt  bmi  hc  gen  phb  tv  reg
  4   1  hgt  wgt  bmi  hc  gen  phb  tv  reg
  4   2  hgt  wgt  bmi  hc  gen  phb  tv  reg
  4   3  hgt  wgt  bmi  hc  gen  phb  tv  reg
  4   4  hgt  wgt  bmi  hc  gen  phb  tv  reg
  4   5  hgt  wgt  bmi  hc  gen  phb  tv  reg
  5   1  hgt  wgt  bmi  hc  gen  phb  tv  reg
  5   2  hgt  wgt  bmi  hc  gen  phb  tv  reg
  5   3  hgt  wgt  bmi  hc  gen  phb  tv  reg
  5   4  hgt  wgt  bmi  hc  gen  phb  tv  reg
  5   5  hgt  wgt  bmi  hc  gen  phb  tv  reg"""


def _calc_bmi(data: np.ndarray, names: list[str]) -> np.ndarray:
    wgt = data[:, names.index("wgt")]
    hgt = data[:, names.index("hgt")]
    return wgt / (hgt / 100.0) ** 2


def _tv_table(mids, names: list[str]) -> str:
    tv_i = names.index("tv")
    tv = complete(mids, 1)[:, tv_i]
    tv = tv[np.isfinite(tv)]
    rounded = np.round(tv).astype(int)
    levels, counts = np.unique(rounded, return_counts=True)
    order = np.argsort(levels)
    return format_table_r(levels[order].tolist(), counts[order].tolist())


def run() -> VignetteReport:
    ms_data, ms_names = load_mammalsleep_impute()
    boys, boy_names = load_boys_impute()

    ini_ms = mice(ms_data, column_names=ms_names, maxit=0, m=5, seed=123, print_flag=False)
    pred_ms = ini_ms.predictor_matrix.copy()
    pred_ms_mod = pred_ms.copy()
    for row in ("sws", "ps"):
        pred_ms_mod[ms_names.index(row), ms_names.index("ts")] = 0

    meth_ms = dict(ini_ms.method)
    meth_ms["ts"] = "~ I(sws + ps)"
    pas_imp = mice(
        ms_data,
        column_names=ms_names,
        method=meth_ms,
        predictor_matrix=pred_ms_mod,
        m=5,
        maxit=10,
        seed=123,
        print_flag=False,
    )

    ts_i = ms_names.index("ts")
    sws_i = ms_names.index("sws")
    ps_i = ms_names.index("ps")
    miss_ts = np.isnan(ms_data[:, ts_i])
    filled_pas = complete(pas_imp, 1)
    pas_err = float(
        np.max(
            np.abs(
                filled_pas[miss_ts, ts_i] - (filled_pas[miss_ts, sws_i] + filled_pas[miss_ts, ps_i])
            )
        )
    )

    imp_pmm = mice(boys, column_names=boy_names, m=5, maxit=5, seed=123, print_flag=False)

    ini_boys = mice(boys, column_names=boy_names, maxit=0, seed=123, print_flag=False)
    meth_tv = dict(ini_boys.method)
    meth_tv["tv"] = "norm"
    imp_norm_post = mice(
        boys,
        column_names=boy_names,
        method=meth_tv,
        post={"tv": post_squeeze(1, 25)},
        m=5,
        maxit=5,
        seed=123,
        print_flag=False,
    )
    meth_boys = dict(ini_boys.method)
    meth_boys["bmi"] = "~ I(wgt / (hgt / 100)^2)"
    pred_boys = ini_boys.predictor_matrix.copy()
    pred_boys_mod = pred_boys.copy()
    for row in ("hgt", "wgt"):
        pred_boys_mod[boy_names.index(row), boy_names.index("bmi")] = 0

    imp_bmi_circ = mice(
        boys,
        column_names=boy_names,
        method=meth_boys,
        m=5,
        maxit=5,
        seed=123,
        print_flag=False,
    )
    imp_bmi = mice(
        boys,
        column_names=boy_names,
        method=meth_boys,
        predictor_matrix=pred_boys_mod,
        m=5,
        maxit=5,
        seed=123,
        print_flag=False,
    )

    meth_path = dict(ini_boys.method)
    meth_path["bmi"] = "~ I(wgt/(hgt/100)^2)"
    meth_path["wgt"] = "~ I(bmi*(hgt/100)^2)"
    meth_path["hgt"] = "~ I(sqrt(wgt/bmi)*100)"
    mice(
        boys,
        column_names=boy_names,
        method=meth_path,
        predictor_matrix=pred_boys,
        m=5,
        maxit=5,
        seed=123,
        print_flag=False,
    )

    bmi_i = boy_names.index("bmi")
    np.isnan(boys[:, bmi_i])

    ASSETS.mkdir(parents=True, exist_ok=True)
    trace_pas = save_figure(
        plot_mids(pas_imp, variables=["ts", "sws", "ps"]),
        ASSETS,
        "v04_passive_trace.png",
    )
    density_pmm = save_figure(plot_density(imp_pmm, "tv"), ASSETS, "v04_density_tv_pmm.png")
    density_norm_post = save_figure(
        plot_density(imp_norm_post, "tv"),
        ASSETS,
        "v04_density_tv_norm_post.png",
    )
    xy_default = save_figure(
        plot_xy_imputed(
            imp_pmm,
            "bmi",
            _calc_bmi(complete(imp_pmm, 1), boy_names),
        ),
        ASSETS,
        "v04_xy_bmi_default.png",
    )
    xy_circ = save_figure(
        plot_xy_imputed(
            imp_bmi_circ,
            "bmi",
            _calc_bmi(complete(imp_bmi_circ, 1), boy_names),
        ),
        ASSETS,
        "v04_xy_bmi_circ.png",
    )
    trace_bmi_circ = save_figure(
        plot_mids(imp_bmi_circ, variables=["bmi"]),
        ASSETS,
        "v04_trace_bmi_circ.png",
    )
    xy_fixed = save_figure(
        plot_xy_imputed(
            imp_bmi,
            "bmi",
            _calc_bmi(complete(imp_bmi, 1), boy_names),
        ),
        ASSETS,
        "v04_xy_bmi_fixed.png",
    )
    trace_bmi_fixed = save_figure(
        plot_mids(imp_bmi, variables=["bmi"]),
        ASSETS,
        "v04_trace_bmi_fixed.png",
    )

    b = VignetteBuilder("04", "v04_passive", TITLE, URL)
    b.set_intro(load_intro(), authors=AUTHORS, series_label=SERIES_LABEL)
    b.set_disclaimer(GLOBAL_DISCLAIMER)
    b.set_parity_overview(V04_PARITY_OVERVIEW)

    b.numbered_section(
        1,
        load_step_title(1),
        [
            TutorialPart(
                r_code="require(mice)\nrequire(lattice)\nset.seed(123)",
                r_expected=R_SETUP,
                python_code=(
                    "import numpy as np\n"
                    "from pymice import mice, complete, post_squeeze\n"
                    "from pymice.diagnostics.plots import plot_density, plot_mids, plot_xy_imputed\n"
                    "from lib.data import load_mammalsleep_impute, load_boys_impute\n"
                    "from lib.viz import save_figure\n"
                    "from lib.r_style import format_meth_r, format_predictor_matrix, format_table_r"
                ),
                run=lambda: "(setup — no console output)",
                partial=True,
                partial_reason="Package load step; no R console output to compare.",
                narrative_after=N1_AFTER + "\n\n" + N1_PASSIVE,
            ),
        ],
    )

    b.numbered_section(
        2,
        load_step_title(2),
        [
            TutorialPart(
                r_code="ini <- mice(mammalsleep[, -1], maxit=0, print=F)\nmeth<- ini$meth\nmeth",
                python_code=(
                    "ini_ms = mice(ms_data, column_names=ms_names, maxit=0, seed=123, print_flag=False)\n"
                    "print(format_meth_r(ms_names, ini_ms.method, style='mammalsleep'))"
                ),
                run=lambda: format_meth_r(ms_names, ini_ms.method, style="mammalsleep"),
                r_expected=R_METH_MS,
                exact=True,
            ),
            TutorialPart(
                r_code="pred <- ini$pred\npred",
                python_code="print(format_predictor_matrix(ms_names, ini_ms.predictor_matrix))",
                run=lambda: format_predictor_matrix(ms_names, ini_ms.predictor_matrix),
                r_expected=R_PRED_MS,
                exact=True,
            ),
            TutorialPart(
                r_code='pred[c("sws", "ps"), "ts"] <- 0\npred',
                python_code=(
                    "pred_ms_mod = pred_ms.copy()\n"
                    'for row in ("sws", "ps"):\n'
                    '    pred_ms_mod[ms_names.index(row), ms_names.index("ts")] = 0\n'
                    "print(format_predictor_matrix(ms_names, pred_ms_mod))"
                ),
                run=lambda: format_predictor_matrix(ms_names, pred_ms_mod),
                r_expected=R_PRED_MS_MOD,
                exact=True,
            ),
            TutorialPart(
                r_code='meth["ts"]<- "~ I(sws + ps)"\n'
                "pas.imp <- mice(mammalsleep[, -1], meth=meth, pred=pred, maxit=10, seed=123, print=F)",
                python_code=(
                    'meth_ms["ts"] = "~ I(sws + ps)"\n'
                    "pas_imp = mice(ms_data, column_names=ms_names, method=meth_ms, "
                    "predictor_matrix=pred_ms_mod, m=5, maxit=10, seed=123, print_flag=False)"
                ),
                run=lambda: f"max |ts - (sws+ps)| on imputed rows: {pas_err:.2e}",
                r_expected="max |ts - (sws+ps)| on imputed rows: 0.00e+00",
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
                r_code="plot(pas.imp)",
                python_code="plot_mids(pas_imp, variables=['ts', 'sws', 'ps'])",
                is_plot=True,
                narrative_after=N3_AFTER + "\n\n" + N3_POST,
            ),
        ],
        images=[trace_pas],
    )

    b.part(PART_POST)

    b.numbered_section(
        4,
        load_step_title(4),
        [
            TutorialPart(
                r_code=(
                    "ini <- mice(boys, maxit = 0)\n"
                    "meth <- ini$meth\n"
                    'meth["tv"] <- "norm"\n'
                    "post <- ini$post\n"
                    'post["tv"] <- "imp[[j]][, i] <- squeeze(imp[[j]][, i], c(1, 25))"\n'
                    "imp <- mice(boys, meth=meth, post=post, print=FALSE)"
                ),
                r_expected=R_MICE_BOYS_PASSIVE,
                python_code=(
                    "meth_tv = dict(ini_boys.method); meth_tv['tv'] = 'norm'\n"
                    "imp_norm_post = mice(boys, column_names=boy_names, method=meth_tv, "
                    "post={'tv': post_squeeze(1, 25)}, m=5, maxit=5, seed=123)"
                ),
                run=lambda: "(imp created — no console output)",
                partial=True,
                partial_reason="Constrained `norm` imputation via `post_squeeze(1, 25)`.",
                narrative_after=N4_AFTER,
            ),
        ],
    )

    b.numbered_section(
        5,
        load_step_title(5),
        [
            TutorialPart(
                narrative_before=N5_BEFORE_PMM,
                r_code="imp.pmm <- mice(boys, print=FALSE)",
                r_expected=R_MICE_PMM,
                python_code=(
                    "imp_pmm = mice(boys, column_names=boy_names, m=5, maxit=5, "
                    "seed=123, print_flag=False)"
                ),
                run=lambda: "(pmm imputation — no printed output)",
                partial=True,
                partial_reason="Creates `imp.pmm` object; R vignette prints no console output here.",
            ),
            TutorialPart(
                r_code="table(complete(imp)$tv)",
                r_expected=R_TABLE_TV,
                python_code="print(_tv_table(imp_norm_post, boy_names))",
                run=lambda: _tv_table(imp_norm_post, boy_names),
                partial=True,
                partial_reason="Squeezed `tv` counts differ under norm RNG (`seed=123`).",
            ),
            TutorialPart(
                r_code="table(complete(imp.pmm)$tv)",
                python_code="print(_tv_table(imp_pmm, boy_names))",
                run=lambda: _tv_table(imp_pmm, boy_names),
                r_expected=R_TABLE_PMM,
                partial=True,
                partial_reason="PMM `tv` counts may differ slightly under seed=123.",
                narrative_after=N5_AFTER_NORM,
            ),
            TutorialPart(
                r_code="densityplot(imp, ~tv)",
                r_expected=R_MICE_BOYS_PASSIVE,
                python_code="plot_density(imp_norm_post, 'tv')",
                is_plot=True,
                plot_note="Density of post-squeezed norm `tv` imputations.",
            ),
            TutorialPart(
                narrative_before=N5_AFTER_DENSITY,
                r_code=(
                    "tv <- c(complete(imp.pmm)$tv, complete(imp)$tv)\n"
                    'method <- rep(c("pmm", "norm"), each = nrow(boys))\n'
                    "tvm <- data.frame(tv = tv, method = method)\n"
                    "histogram( ~tv | method, data = tvm, nint = 25)"
                ),
                python_code="plot_density(imp_pmm, 'tv')  # pmm-only partial diagnostic",
                is_plot=True,
                plot_note="Post-processed norm comparison skipped; PMM density shown.",
                narrative_after=N5_AFTER_HIST,
            ),
        ],
        images=[density_pmm, density_norm_post],
    )

    b.numbered_section(
        6,
        load_step_title(6),
        [
            TutorialPart(
                r_code=(
                    "miss <- is.na(imp$data$bmi)\n"
                    "xyplot(imp, bmi ~ I (wgt / (hgt / 100)^2),\n"
                    "       na.groups = miss, cex = c(0.8, 1.2), pch = c(1, 20),\n"
                    '       ylab = "BMI (kg/m2) Imputed", xlab = "BMI (kg/m2) Calculated")'
                ),
                r_expected=R_MICE_BOYS_BMI,
                python_code=(
                    "miss_bmi = np.isnan(boys[:, boy_names.index('bmi')])\n"
                    "plot_xy_imputed(imp_pmm, 'bmi', _calc_bmi(complete(imp_pmm, 1), boy_names))"
                ),
                is_plot=True,
                plot_note="Uses default `pmm` imputation (`imp.pmm`) — step 4 `imp` not available.",
                narrative_after=N6_AFTER,
            ),
        ],
        images=[xy_default],
    )

    b.numbered_section(
        7,
        load_step_title(7),
        [
            TutorialPart(
                r_code=(
                    "meth<- ini$meth\n"
                    'meth["bmi"]<- "~ I(wgt / (hgt / 100)^2)"\n'
                    "imp <- mice(boys, meth=meth, print=FALSE)"
                ),
                r_expected=R_MICE_BOYS_BMI,
                python_code=(
                    'meth_boys["bmi"] = "~ I(wgt / (hgt / 100)^2)"\n'
                    "imp_bmi_circ = mice(boys, column_names=boy_names, method=meth_boys, "
                    "m=5, maxit=5, seed=123, print_flag=False)"
                ),
                run=lambda: "(passive `bmi` imputation — no printed output)",
                partial=True,
                partial_reason="Creates `imp` with passive `bmi`; circularity not yet fixed.",
            ),
        ],
    )

    b.numbered_section(
        8,
        load_step_title(8),
        [
            TutorialPart(
                narrative_before=N8_BEFORE_XY,
                r_code=(
                    "xyplot(imp, bmi ~ I(wgt / (hgt / 100)^2), na.groups = miss,\n"
                    "       cex = c(1, 1), pch = c(1, 20),\n"
                    '       ylab = "BMI (kg/m2) Imputed", xlab = "BMI (kg/m2) Calculated")'
                ),
                r_expected=R_MICE_BOYS_BMI,
                python_code=(
                    "plot_xy_imputed(imp_bmi_circ, 'bmi', "
                    "_calc_bmi(complete(imp_bmi_circ, 1), boy_names))"
                ),
                is_plot=True,
            ),
            TutorialPart(
                narrative_before=N8_BEFORE_PLOT,
                r_code='plot(imp, c("bmi"))',
                python_code="plot_mids(imp_bmi_circ, variables=['bmi'])",
                is_plot=True,
                narrative_after=N7_AFTER,
            ),
        ],
        images=[xy_circ, trace_bmi_circ],
    )

    b.numbered_section(
        9,
        load_step_title(9),
        [
            TutorialPart(
                narrative_before=N9_BEFORE_PRED,
                r_code="pred<-ini$pred\npred",
                python_code="print(format_predictor_matrix(boy_names, ini_boys.predictor_matrix))",
                run=lambda: format_predictor_matrix(boy_names, ini_boys.predictor_matrix),
                r_expected=R_PRED_BOYS,
                exact=True,
            ),
            TutorialPart(
                r_code='pred[c("hgt", "wgt"), "bmi"] <- 0\npred',
                python_code=("print(format_predictor_matrix(boy_names, pred_boys_mod))"),
                run=lambda: format_predictor_matrix(boy_names, pred_boys_mod),
                r_expected=R_PRED_BOYS_MOD,
                exact=True,
                narrative_after=N9_AFTER_PRED,
            ),
            TutorialPart(
                r_code="imp <-mice(boys, meth=meth, pred=pred, print=FALSE)",
                r_expected=R_MICE_BOYS_METH,
                python_code=(
                    "imp_bmi = mice(boys, column_names=boy_names, method=meth_boys, "
                    "predictor_matrix=pred_boys_mod, m=5, maxit=5, seed=123, print_flag=False)"
                ),
                run=lambda: "(imputation with fixed predictor matrix — no printed output)",
                partial=True,
                partial_reason="R vignette shows code only before diagnostic plots.",
            ),
            TutorialPart(
                narrative_before=N9_BEFORE_XY,
                r_code=(
                    "xyplot(imp, bmi ~ I(wgt / (hgt / 100)^2), na.groups = miss,\n"
                    "       cex=c(1, 1), pch=c(1, 20),\n"
                    '       ylab="BMI (kg/m2) Imputed", xlab="BMI (kg/m2) Calculated")'
                ),
                r_expected=R_MICE_BOYS_BMI,
                python_code=(
                    "plot_xy_imputed(imp_bmi, 'bmi', _calc_bmi(complete(imp_bmi, 1), boy_names))"
                ),
                is_plot=True,
            ),
            TutorialPart(
                narrative_before=N9_BEFORE_TRACE,
                r_code='plot(imp, c("bmi"))',
                python_code="plot_mids(imp_bmi, variables=['bmi'])",
                is_plot=True,
                narrative_after=N9_AFTER_OK,
            ),
            TutorialPart(
                narrative_before=N9_CONCLUSION + "\n\n" + N9_FUN,
                r_code=(
                    "ini <- mice(boys, maxit=0)\n"
                    "meth<- ini$meth\n"
                    "pred <- ini$pred\n"
                    'meth["bmi"]<- "~ I(wgt/(hgt/100)^2)"\n'
                    'meth["wgt"]<- "~ I(bmi*(hgt/100)^2)"\n'
                    'meth["hgt"]<- "~ I(sqrt(wgt/bmi)*100)"\n'
                    "imp.path <- mice(boys, meth=meth, pred=pred, seed=123)"
                ),
                r_expected=R_MICE_PATH,
                python_code=(
                    "meth_path = dict(ini_boys.method)\n"
                    'meth_path["bmi"] = "~ I(wgt/(hgt/100)^2)"\n'
                    'meth_path["wgt"] = "~ I(bmi*(hgt/100)^2)"\n'
                    'meth_path["hgt"] = "~ I(sqrt(wgt/bmi)*100)"\n'
                    "imp_path = mice(boys, column_names=boy_names, method=meth_path, "
                    "predictor_matrix=pred_boys, m=5, maxit=5, seed=123, print_flag=False)"
                ),
                run=lambda: "(triple passive imputation — no printed output)",
                partial=True,
                partial_reason="R vignette prints iteration log; PyMICE runs imputation without event log.",
            ),
            TutorialPart(
                r_code='plot(imp.path, c("hgt", "wgt", "bmi"))',
                r_expected=R_MICE_PATH,
                python_code="plot_mids(imp_path, variables=['hgt', 'wgt', 'bmi'])",
                is_plot=True,
                narrative_after=N9_FUN_AFTER,
            ),
        ],
        images=[xy_fixed, trace_bmi_fixed],
    )

    return b.build()
