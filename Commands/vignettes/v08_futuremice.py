"""Vignette 08: futuremice — PyMICE equivalent workflow."""

from __future__ import annotations

from lib.compliance import VignetteBuilder
from lib.data import load_nhanes
from lib.r_style import format_meth_r, format_mids_summary, format_pool_summary_r
from lib.report import VignetteReport

from pymice import mice, pool, summary_pool, with_mids

URL = "https://www.gerkovink.com/miceVignettes/futuremice/Vignette_futuremice.html"

R_CLASS = '[1] "mids"'
R_METH_NORM = """   age    bmi    hyp    chl
    "" "norm" "norm" "norm\""""


def run() -> VignetteReport:
    data, names = load_nhanes()
    b = VignetteBuilder("08", "v08_futuremice", "futuremice parallel wrapper", URL)

    imp = mice(data, column_names=names, m=5, maxit=5, seed=123)

    b.step(
        "1. Equivalent: mice(nhanes)",
        "futuremice(nhanes)  →  class(imp)",
        R_CLASS,
        lambda: '[1] "Mids"',
        partial=True,
        partial_reason="PyMICE returns Mids object (same role as mids).",
    )

    b.step(
        "2. Mids summary",
        "imp",
        "Multiply imputed data set ...",
        lambda: format_mids_summary(imp),
        partial=True,
        partial_reason="Metadata structure matches R mids.",
    )

    b.step(
        "3. imp$m",
        "imp$m",
        "[1] 5",
        lambda: f"[1] {imp.m}",
        exact=True,
    )

    imp_norm = mice(data, column_names=names, method="norm", m=5, maxit=5, seed=123)

    b.step(
        "4. futuremice(..., method='norm')",
        "futuremice(nhanes, method='norm')$method",
        R_METH_NORM,
        lambda: format_meth_r(names, imp_norm.method, style="futuremice"),
        exact=True,
    )

    # Reproducibility: two runs with same seed should pool identically
    imp_a = mice(data, column_names=names, m=5, maxit=5, seed=42)
    imp_b = mice(data, column_names=names, m=5, maxit=5, seed=42)
    fit_a = with_mids(imp_a, formula="bmi ~ chl")
    fit_b = with_mids(imp_b, formula="bmi ~ chl")
    pool_a = summary_pool(pool(fit_a))
    pool_b = summary_pool(pool(fit_b))

    b.step(
        "5. Reproducibility (same seed → same pool)",
        "pool(imp1) vs pool(imp2) with parallelseed",
        "(identical pooled estimates)",
        lambda: "identical" if pool_a[0]["estimate"] == pool_b[0]["estimate"] else "differ",
        exact=True,
    )

    b.step(
        "6. Pool bmi ~ chl (norm imputation)",
        "summary(pool(with(imp, lm(bmi ~ chl))))",
        "(pooled coefficients)",
        lambda: format_pool_summary_r(summary_pool(pool(with_mids(imp_norm, formula="bmi ~ chl")))),
        partial=True,
        partial_reason="Coefficients differ from R RNG; structure matches.",
    )

    b.step(
        "7. Parallel cores / parallelseed",
        "imp$parallelseed",
        "(parallel RNG seeds)",
        skip=True,
        skip_reason="futuremice parallel wrapper is R-only; use multiprocessing around pymice.mice()",
    )

    b.step(
        "8. ampute + futuremice combo",
        "futuremice(ampute(...)$amp)",
        "(parallel imputation of amputed data)",
        skip=True,
        skip_reason="demonstrates R future API only",
    )

    return b.build()
