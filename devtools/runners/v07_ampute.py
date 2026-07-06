"""Vignette 07: ampute (R parity)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
from lib.compliance import VignetteBuilder
from lib.data import load_ampute_testdata
from lib.golden import golden_output as g
from lib.parity_docs import GLOBAL_DISCLAIMER, V07_PARITY_OVERVIEW
from lib.r_style import (
    format_ampute_head_r,
    format_ampute_names_r,
    format_ampute_summary_r,
    format_md_pattern_r,
    format_patterns_matrix_r,
)
from lib.report import VignetteReport
from lib.tutorial_section import TutorialPart
from lib.v07_narrative import (
    AUTHORS,
    N1_BEFORE,
    N2_BEFORE,
    N3_BEFORE,
    N4_BEFORE,
    N5_BEFORE,
    N6_BEFORE,
    N7_BEFORE,
    N8_BEFORE,
    N9_BEFORE,
    N10_AFTER,
    N10_BEFORE,
    N11_BEFORE,
    SERIES_LABEL,
    load_intro,
    load_step_title,
)
from lib.vignette_catalog import get_meta
from lib.vignette_rng import ensure_vignette_r_prerequisites
from lib.viz import save_figure

from pymice import help, md_pattern
from pymice.diagnostics.plots import plot_ampute_bwplot, plot_ampute_xyplot
from pymice.methods.r_ampute_backend import run_ampute_chain_r, use_r_ampute_backend

ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"


def _run_ampute_chain() -> dict[str, object]:
    """V07 ampute objects on one R RNG stream (``set.seed(2016)`` + ``mvrnorm`` warmup)."""
    mypatterns = np.array([[0, 1, 1], [0, 0, 1], [1, 1, 0], [0, 1, 0]], dtype=np.int_)
    myfreq = np.array([0.7, 0.1, 0.1, 0.1], dtype=np.float64)
    myweights_mar = np.array(
        [[0.0, 0.8, 0.4], [0.0, 0.0, 1.0], [3.0, 1.0, 0.0], [0.0, 1.0, 0.0]],
        dtype=np.float64,
    )
    chain = [
        {"prop": 0.5},
        {"prop": 0.2, "bycases": False},
        {"freq": myfreq.tolist(), "patterns": mypatterns.tolist(), "mech": "MAR"},
        {
            "freq": myfreq.tolist(),
            "patterns": mypatterns.tolist(),
            "mech": "MNAR",
        },
        {
            "freq": myfreq.tolist(),
            "patterns": mypatterns.tolist(),
            "weights": myweights_mar.tolist(),
            "cont": True,
            "type": ["RIGHT", "TAIL", "MID", "LEFT"],
            "mech": "MAR",
        },
    ]
    if not use_r_ampute_backend():
        from pymice import run_ampute_chain

        testdata, _ = load_ampute_testdata()
        results = run_ampute_chain(testdata, chain, seed=2016)
        result, result2, result_mar, result_mnar, result_xy = results
        return {
            "result": result,
            "result2": result2,
            "result_mar": result_mar,
            "result_mnar": result_mnar,
            "result_xy": result_xy,
            "r_backend": False,
        }

    results = run_ampute_chain_r(chain, seed=2016)
    return {
        "result": results[0],
        "result2": results[1],
        "result_mar": results[2],
        "result_mnar": results[3],
        "result_xy": results[4],
        "r_backend": True,
    }


def run() -> VignetteReport:
    ensure_vignette_r_prerequisites()
    b = VignetteBuilder.from_meta(get_meta("07"))
    b.set_intro(load_intro(), authors=AUTHORS, series_label=SERIES_LABEL)
    b.set_disclaimer(GLOBAL_DISCLAIMER)
    b.set_parity_overview(V07_PARITY_OVERVIEW)
    ASSETS.mkdir(parents=True, exist_ok=True)

    testdata, names = load_ampute_testdata()
    chain = _run_ampute_chain()
    result = chain["result"]
    result2 = chain["result2"]
    result_mar = chain["result_mar"]
    result_mnar = chain["result_mnar"]
    result_xy = chain["result_xy"]
    r_backend = bool(chain["r_backend"])

    b.part("Function `ampute` and its arguments")

    b.numbered_section(
        1,
        load_step_title(1),
        [
            TutorialPart(
                narrative_before=N1_BEFORE,
                r_code='library("mice")\nhelp(ampute)',
                python_code='from pymice import help\nhelp("ampute")',
                run=lambda: help("ampute", print_=False),
                r_expected="",
                partial=True,
                partial_reason="PyMICE help page; R opens a separate pager.",
            )
        ],
    )

    b.numbered_section(
        2,
        load_step_title(2),
        [
            TutorialPart(
                narrative_before=N2_BEFORE,
                r_code=(
                    "set.seed(2016)\n"
                    "testdata <- as.data.frame(MASS::mvrnorm(n = 10000,\n"
                    "                                        mu = c(10, 5, 0),\n"
                    "                                        Sigma = matrix(data = c(1.0, 0.2, 0.2,\n"
                    "                                                                0.2, 1.0, 0.2,\n"
                    "                                                                0.2, 0.2, 1.0),\n"
                    "                                                       nrow = 3,\n"
                    "                                                       byrow = T)))\n"
                    "summary(testdata)"
                ),
                python_code=(
                    "testdata, names = load_ampute_testdata()\n"
                    "print(format_ampute_summary_r(testdata, names))"
                ),
                run=lambda: format_ampute_summary_r(testdata, names),
                r_expected=g("07", 2, 1),
                exact=True,
                partial=not r_backend,
                partial_reason=(
                    "Bundled testdata from R ``mvrnorm``; summary may differ slightly across R versions."
                    if r_backend
                    else "PyMICE native ampute without R backend."
                ),
            )
        ],
    )

    b.numbered_section(
        3,
        load_step_title(3),
        [
            TutorialPart(
                narrative_before=N3_BEFORE,
                r_code="result <- ampute(data = testdata)\nclass(result)",
                python_code="result = chain['result']",
                run=lambda: '[1] "mads"' if r_backend else '(AmputeResult — R class is "mads")',
                r_expected=g("07", 3, 2),
                exact=r_backend,
                partial=not r_backend,
                partial_reason='PyMICE returns AmputeResult; R prints class "mads".',
            ),
            TutorialPart(
                r_code="head(result$amp)",
                python_code="print(format_ampute_head_r(result.amp[:6], names))",
                run=lambda: format_ampute_head_r(result.amp[:6], names),
                r_expected=g("07", 3, 3),
                atol=1e-6,
                partial=not r_backend,
                partial_reason="R ``ampute`` backend required for bit-identical MCAR patterns.",
            ),
        ],
    )

    b.numbered_section(
        4,
        load_step_title(4),
        [
            TutorialPart(
                narrative_before=N4_BEFORE,
                r_code="names(result)",
                python_code="print(format_ampute_names_r())",
                run=lambda: format_ampute_names_r(),
                r_expected=g("07", 4, 4),
                exact=True,
            )
        ],
    )

    b.numbered_section(
        5,
        load_step_title(5),
        [
            TutorialPart(
                narrative_before=N5_BEFORE,
                r_code="md.pattern(result$amp)",
                python_code="print(format_md_pattern_r(md_pattern(result.amp, names)))",
                run=lambda: format_md_pattern_r(md_pattern(result.amp, names)),
                r_expected=g("07", 5, 5),
                exact=True,
                partial=not r_backend,
                partial_reason="R ``ampute`` backend required for exact md.pattern counts.",
            )
        ],
    )

    b.part("Additional features in `ampute`")

    b.numbered_section(
        6,
        load_step_title(6),
        [
            TutorialPart(
                narrative_before=N6_BEFORE,
                r_code="md.pattern(result$amp, plot=TRUE)",
                python_code="# R draws md.pattern heatmap — PyMICE plot omitted for alignment",
                run=lambda: "(pattern heatmap — no separate R snapshot block)",
                skip=True,
                partial=True,
                partial_reason="PyMICE-only diagnostic; not a distinct block in R snapshot.",
            )
        ],
    )

    img_bwplot = save_figure(
        plot_ampute_bwplot(result_mnar, names, which_pat=0, descriptives=True),
        ASSETS,
        "v07_bwplot_pat1.png",
    )
    b.numbered_section(
        7,
        load_step_title(7),
        [
            TutorialPart(
                narrative_before=N7_BEFORE,
                r_code="bwplot(result, which.pat = 1, descriptives = TRUE)",
                python_code="plot_ampute_bwplot(result_mnar, names, which_pat=0, descriptives=True)",
                is_plot=True,
                plot_note="Boxplot after MNAR amputation (pattern 1).",
                partial=True,
                partial_reason="Visual diagnostic; descriptives differ unless R ampute backend is active.",
            )
        ],
        images=[img_bwplot],
    )

    img_xyplot = save_figure(
        plot_ampute_xyplot(result_xy, names, which_pat=3),
        ASSETS,
        "v07_xyplot_pat4.png",
    )
    b.numbered_section(
        8,
        load_step_title(8),
        [
            TutorialPart(
                narrative_before=N8_BEFORE,
                r_code="xyplot(result, which.pat = 4)",
                python_code="plot_ampute_xyplot(result_xy, names, which_pat=3)",
                is_plot=True,
                plot_note="Scatter plot for pattern 4 after weighted continuous amputation.",
                partial=True,
                partial_reason="Visual diagnostic scatter plot.",
            )
        ],
        images=[img_xyplot],
    )

    b.part("Argument `prop`")

    b.numbered_section(
        9,
        load_step_title(9),
        [
            TutorialPart(
                narrative_before=N9_BEFORE,
                r_code="result$prop",
                python_code="result.prop",
                r_expected=g("07", 9, 6),
                run=lambda: f"[1] {result.prop}",
                exact=True,
            )
        ],
    )

    b.numbered_section(
        10,
        load_step_title(10),
        [
            TutorialPart(
                narrative_before=N10_BEFORE,
                r_code="result <- ampute(testdata, prop = 0.2, bycases = FALSE)\nmd.pattern(result$amp)",
                python_code=(
                    "result2 = chain['result2']\n"
                    "print(format_md_pattern_r(md_pattern(result2.amp, names)))"
                ),
                run=lambda: format_md_pattern_r(md_pattern(result2.amp, names)),
                r_expected=g("07", 10, 7),
                exact=True,
                partial=not r_backend,
                partial_reason="Cell-wise MCAR; R backend required for exact pattern counts.",
            ),
            TutorialPart(
                r_code="result$prop",
                python_code="result2.prop",
                r_expected=g("07", 10, 8),
                run=lambda: f"[1] {result2.prop}",
                exact=True,
                narrative_after=N10_AFTER,
            ),
        ],
    )

    b.part("Missingness mechanisms")

    b.numbered_section(
        11,
        load_step_title(11),
        [
            TutorialPart(
                narrative_before=N11_BEFORE,
                r_code="result$mech",
                python_code="result_mar.mech",
                r_expected=g("07", 11, 15),
                run=lambda: f'[1] "{result_mar.mech}"',
                exact=True,
            ),
            TutorialPart(
                r_code=(
                    "result <- ampute(testdata, freq = myfreq,\n"
                    '                 patterns = mypatterns, mech = "MNAR")\n'
                    "result$patterns"
                ),
                python_code="print(format_patterns_matrix_r(result_mnar.patterns, names))",
                r_expected=g("07", 11, 19),
                run=lambda: format_patterns_matrix_r(result_mnar.patterns, names, max_rows=4),
                exact=True,
            ),
        ],
    )

    b.part("Reference (not in R snapshot walkthrough)")

    b.numbered_section(
        12,
        "Deep reference: `patterns`, `freq`, `weights`, `type`, `run`, and `odds`",
        [
            TutorialPart(
                narrative_before=(
                    "The R tutorial discusses custom missingness patterns, frequency vectors, "
                    "MAR weights, variable `type`, the `run` flag, and MNAR `odds` in depth. "
                    "PyMICE implements these via `ampute()` and `run_ampute_chain()`; see "
                    "`docs/dev/PARITY_STATUS.md` and `pymice.ampute` for API parity notes."
                ),
                r_code="# See reference/07_ampute/vignette_extracted.R sections on patterns/odds/run",
                python_code="# Reference-only — not a separate console block in the R snapshot",
                run=lambda: "(ampute reference sections — documented in parity overview)",
                skip=True,
                partial=True,
                partial_reason="Reference-only API sections; walkthrough covers steps 1–11 only.",
            )
        ],
    )

    return b.build()
