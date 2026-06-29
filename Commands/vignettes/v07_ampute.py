"""Vignette 07: ampute (R parity)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
from lib.compliance import VignetteBuilder
from lib.r_style import format_dataframe_r, format_md_pattern_r, format_summary_r
from lib.report import VignetteReport
from lib.viz import save_figure
from scipy.linalg import cholesky

from pymice import ampute, help, md_pattern
from pymice.diagnostics.plots import plot_ampute_bwplot, plot_ampute_xyplot, plot_md_pattern

URL = "https://rianneschouten.github.io/mice_ampute/vignette/ampute.html"
ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"

R_SUMMARY = """       V1
  Min.   : 6.346
  Mean   : 9.998
       V2
  Min.   :0.9789
  Mean   :4.9973
       V3
  Min.   :-3.799124
  Mean   : 0.000759"""

R_MDP_DEFAULT = """5014    1    1    1    0
1670    1    1    0    1
1670    1    0    1    1
1646    0    1    1    1
     1646 1670 1670 4986"""


def _r_testdata(seed: int = 2016) -> np.ndarray:
    """MASS::mvrnorm testdata from vignette (seed 2016)."""
    rng = np.random.default_rng(seed)
    sigma = np.array([[1.0, 0.2, 0.2], [0.2, 1.0, 0.2], [0.2, 0.2, 1.0]])
    mu = np.array([10.0, 5.0, 0.0])
    chol = cholesky(sigma)
    z = rng.standard_normal((10000, 3))
    return z @ chol.T + mu


def run() -> VignetteReport:
    b = VignetteBuilder("07", "v07_ampute", "Generate missing values with ampute", URL)
    ASSETS.mkdir(parents=True, exist_ok=True)

    testdata = _r_testdata(2016)
    names = ["V1", "V2", "V3"]

    b.step(
        "0. help(ampute)",
        "help(ampute)",
        "(PyMICE help page)",
        lambda: help("ampute", print_=False),
        partial=True,
        partial_reason="PyMICE help page; R opens a separate pager.",
    )

    b.step(
        "1. Summary complete testdata",
        "summary(testdata)",
        R_SUMMARY,
        lambda: "\n".join(format_summary_r(testdata, names).splitlines()[:9]),
        atol=0.05,
        partial=True,
        partial_reason="Summary statistics approximate (RNG stream differs from R set.seed).",
    )

    result = ampute(testdata, prop=0.5, seed=2016)

    b.step(
        "2. head(result$amp)",
        "head(result$amp)",
        "(first rows of amputed data)",
        lambda: format_dataframe_r(result.amp[:6], names),
        partial=True,
        partial_reason="Amputation pattern differs from R; structure shown.",
    )

    b.step(
        "3. Ampute metadata",
        "names(result)",
        "amp patterns freq mech prop bycases",
        lambda: (
            f"fields: amp {result.amp.shape}, patterns {result.patterns.shape}, "
            f"freq={result.freq.tolist()}, mech={result.mech}, prop={result.prop}"
        ),
        partial=True,
        partial_reason="PyMICE AmputeResult vs R mads naming.",
    )

    b.step(
        "4. Default ampute md.pattern",
        "md.pattern(result$amp)",
        R_MDP_DEFAULT,
        lambda: "\n".join(format_md_pattern_r(md_pattern(result.amp, names)).splitlines()[1:6]),
        partial=True,
        partial_reason="MCAR pattern counts differ — simplified ampute algorithm.",
    )

    b.plot_step(
        "5. md.pattern(result$amp) plot",
        "md.pattern(result$amp, plot=TRUE)",
        "Missingness pattern heatmap after amputation.",
        [
            save_figure(
                plot_md_pattern(md_pattern(result.amp, names)),
                ASSETS,
                "v07_amp_mdpattern.png",
            )
        ],
    )

    b.plot_step(
        "6. bwplot(result, which.pat=1)",
        "bwplot(result, which.pat=1, descriptives=TRUE)",
        "Boxplots of amputed vs observed values for pattern 1.",
        [
            save_figure(
                plot_ampute_bwplot(result, names, which_pat=0, descriptives=True),
                ASSETS,
                "v07_bwplot_pat1.png",
            )
        ],
    )

    b.plot_step(
        "7. xyplot(result, which.pat=1)",
        "xyplot(result, which.pat=4)",
        "Scatter of amputed vs observed for pattern 1.",
        [
            save_figure(
                plot_ampute_xyplot(result, names, which_pat=0),
                ASSETS,
                "v07_xyplot_pat1.png",
            )
        ],
    )

    b.step(
        "8. prop = 0.5",
        "result$prop",
        "[1] 0.5",
        lambda: f"[1] {result.prop}",
        exact=True,
    )

    result2 = ampute(testdata, prop=0.2, bycases=False, seed=2016)
    b.step(
        "9. bycases = FALSE",
        "ampute(..., prop=0.2, bycases=FALSE)",
        "per-column amputation",
        lambda: f"missing cells: {int(np.isnan(result2.amp).sum())}",
        partial=True,
        partial_reason="Column-wise MCAR; R reports adjusted prop 0.6.",
    )

    mar = ampute(testdata, mech="MAR", prop=0.5, seed=2016)
    mnar = ampute(testdata, mech="MNAR", prop=0.5, seed=2017)
    b.step(
        "10. MAR / MNAR mechanisms",
        "ampute(..., mech='MAR')",
        "MAR",
        lambda: (
            f"MAR mech={mar.mech}, missing={int(np.isnan(mar.amp).sum())}; "
            f"MNAR mech={mnar.mech}, missing={int(np.isnan(mnar.amp).sum())}"
        ),
        partial=True,
        partial_reason="MAR/MNAR via weighted sum scores + logistic probabilities; RNG differs from R.",
    )

    return b.build()
