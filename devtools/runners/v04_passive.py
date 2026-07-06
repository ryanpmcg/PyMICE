"""Vignette 04: Passive imputation and post-processing — mirrors R tutorial (steps 1–9)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
from lib.compliance import VignetteBuilder
from lib.data import load_boys_impute, load_mammalsleep_impute
from lib.golden import golden_output as g
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
    load_intro,
    load_step_title,
)
from lib.vignette_catalog import get_meta
from lib.vignette_rng import (
    ensure_vignette_r_prerequisites,
    run_v04_chain,
)
from lib.vignette_rng import (
    mice_vignette as mice,
)
from lib.viz import save_figure

from pymice import complete
from pymice.diagnostics.plots import (
    plot_density,
    plot_histogram_facets,
    plot_mids,
    plot_xy_imputed,
)

R_SETUP = ""
R_MICE_BOYS_PASSIVE = ""
R_MICE_PMM = ""
R_MICE_BOYS_BMI = ""
R_MICE_BOYS_METH = ""
R_MICE_PATH = ""


ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"


def _calc_bmi(data: np.ndarray, names: list[str]) -> np.ndarray:
    wgt = data[:, names.index("wgt")]
    hgt = data[:, names.index("hgt")]
    return wgt / (hgt / 100.0) ** 2


def _bmi_passive_check(
    imp,
    raw: np.ndarray,
    names: list[str],
) -> str:
    """Verify passive ``bmi = wgt/(hgt/100)^2`` on rows that were missing in ``raw``."""
    bmi_i = names.index("bmi")
    miss = np.isnan(raw[:, bmi_i])
    filled = complete(imp, 1)
    calc = _calc_bmi(filled, names)
    err = float(np.max(np.abs(filled[miss, bmi_i] - calc[miss])))
    return f"max |bmi - wgt/(hgt/100)^2| on missing rows: {err:.2e}"


def _tv_table(mids, names: list[str]) -> str:
    tv_i = names.index("tv")
    tv = complete(mids, 1)[:, tv_i]
    tv = tv[np.isfinite(tv)]
    rounded = np.round(tv).astype(int)
    levels, counts = np.unique(rounded, return_counts=True)
    order = np.argsort(levels)
    return format_table_r(levels[order].tolist(), counts[order].tolist())


def run() -> VignetteReport:
    ensure_vignette_r_prerequisites()
    ms_data, ms_names = load_mammalsleep_impute()
    boys, boy_names = load_boys_impute()

    chain = run_v04_chain(ms_data, ms_names, boys, boy_names)
    pas_imp = chain["pas_imp"]
    imp_norm_post = chain["imp_norm_post"]
    imp_pmm = chain["imp_pmm"]
    ini_ms = chain["ini_ms"]
    pred_ms_mod = chain["pred_ms_mod"]
    chain["meth_ms"]
    ini_boys = chain["ini_boys"]

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
    imp_bmi_circ = chain["imp_bmi_circ"]
    meth_boys = dict(chain["meth_bmi_circ"])
    pred_boys = ini_boys.predictor_matrix.copy()
    pred_boys_mod = pred_boys.copy()
    for row in ("hgt", "wgt"):
        pred_boys_mod[boy_names.index(row), boy_names.index("bmi")] = 0
    imp_bmi = mice(
        boys,
        column_names=boy_names,
        method=meth_boys,
        predictor_matrix=pred_boys_mod,
        m=5,
        maxit=5,
        print_flag=False,
    )

    meth_path = dict(ini_boys.method)
    meth_path["bmi"] = "~ I(wgt/(hgt/100)^2)"
    meth_path["wgt"] = "~ I(bmi*(hgt/100)^2)"
    meth_path["hgt"] = "~ I(sqrt(wgt/bmi)*100)"
    imp_path = mice(
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
        plot_mids(pas_imp, variables=["sws", "ps", "ts"]),
        ASSETS,
        "v04_passive_trace.png",
    )
    tv_i = boy_names.index("tv")
    density_norm_post = save_figure(
        plot_density(imp_norm_post, "tv"),
        ASSETS,
        "v04_density_tv_norm_post.png",
    )
    hist_tv_method = save_figure(
        plot_histogram_facets(
            {
                "norm": complete(imp_norm_post, 1)[:, tv_i],
                "pmm": complete(imp_pmm, 1)[:, tv_i],
            },
            variable="tv",
            facet_order=["norm", "pmm"],
            n_bins=25,
        ),
        ASSETS,
        "v04_hist_tv_method.png",
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
    trace_imp_path = save_figure(
        plot_mids(imp_path, variables=["hgt", "wgt", "bmi"]),
        ASSETS,
        "v04_trace_imp_path.png",
    )

    b = VignetteBuilder.from_meta(get_meta("04"))
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
                    "from pymice.diagnostics.plots import plot_density, plot_histogram_facets, "
                    "plot_mids, plot_xy_imputed\n"
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
                    "ini_ms = mice(ms_data, column_names=ms_names, maxit=0, print_flag=False)\n"
                    "print(format_meth_r(ms_names, ini_ms.method, style='mammalsleep'))"
                ),
                run=lambda: format_meth_r(ms_names, ini_ms.method, style="mammalsleep"),
                r_expected=g("04", 2, 1),
                exact=True,
            ),
            TutorialPart(
                r_code="pred <- ini$pred\npred",
                python_code="print(format_predictor_matrix(ms_names, ini_ms.predictor_matrix))",
                run=lambda: format_predictor_matrix(ms_names, ini_ms.predictor_matrix),
                r_expected=g("04", 2, 2),
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
                r_expected=g("04", 2, 3),
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
                r_expected="",
                partial=True,
                partial_reason=(
                    "PyMICE verifies circular ts = sws+ps constraint numerically; R prints nothing."
                ),
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
                python_code="plot_mids(pas_imp, variables=['sws', 'ps', 'ts'])",
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
                    "post={'tv': post_squeeze(1, 25)}, m=5, maxit=5, print_flag=False)"
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
                    "imp_pmm = mice(boys, column_names=boy_names, m=5, maxit=5, print_flag=False)"
                ),
                run=lambda: "(pmm imputation — no printed output)",
                partial=True,
                partial_reason="Creates `imp.pmm` object; R vignette prints no console output here.",
            ),
            TutorialPart(
                r_code="table(complete(imp)$tv)",
                r_expected=g("04", 5, 8),
                python_code="print(_tv_table(imp_norm_post, boy_names))",
                run=lambda: _tv_table(imp_norm_post, boy_names),
                exact=True,
            ),
            TutorialPart(
                r_code="table(complete(imp.pmm)$tv)",
                python_code="print(_tv_table(imp_pmm, boy_names))",
                run=lambda: _tv_table(imp_pmm, boy_names),
                r_expected=g("04", 5, 9),
                exact=True,
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
                python_code=(
                    "plot_histogram_facets(\n"
                    "    {'norm': complete(imp_norm_post, 1)[:, tv_i],\n"
                    "     'pmm': complete(imp_pmm, 1)[:, tv_i]},\n"
                    "    variable='tv', facet_order=['norm', 'pmm'], n_bins=25)"
                ),
                is_plot=True,
                narrative_after=N5_AFTER_HIST,
            ),
        ],
        images=[density_norm_post, hist_tv_method],
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
                    "m=5, maxit=5, print_flag=False)"
                ),
                run=lambda: _bmi_passive_check(imp_bmi_circ, boys, boy_names),
                exact=True,
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
                r_expected=g("04", 9, 17),
                exact=True,
            ),
            TutorialPart(
                r_code='pred[c("hgt", "wgt"), "bmi"] <- 0\npred',
                python_code=("print(format_predictor_matrix(boy_names, pred_boys_mod))"),
                run=lambda: format_predictor_matrix(boy_names, pred_boys_mod),
                r_expected=g("04", 9, 18),
                exact=True,
                narrative_after=N9_AFTER_PRED,
            ),
            TutorialPart(
                r_code="imp <-mice(boys, meth=meth, pred=pred, print=FALSE)",
                r_expected=R_MICE_BOYS_METH,
                python_code=(
                    "imp_bmi = mice(boys, column_names=boy_names, method=meth_boys, "
                    "predictor_matrix=pred_boys_mod, m=5, maxit=5, print_flag=False)"
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
                r_expected=g("04", 9, 23),
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
        images=[xy_fixed, trace_bmi_fixed, trace_imp_path],
    )

    return b.build()
