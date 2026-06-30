"""Multivariate pooling across fitted models."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy import stats

from pymice.pool.barnard_rubin import barnard_rubin
from pymice.types import FitResult, Mira, PoolResult


def pool(
    object: Mira | Sequence[FitResult],
    dfcom: float | None = None,
    rule: str = "rubin1987",
) -> PoolResult:
    """Pool estimates from repeated complete-data fits (R ``pool()``)."""
    if isinstance(object, Mira):
        fits = object.analyses
        m = object.m
    else:
        fits = list(object)
        m = len(fits)

    if m == 0:
        raise ValueError("No fitted models to pool")
    if m == 1:
        return _pool_single(fits[0])

    terms = fits[0].terms
    for fit in fits[1:]:
        if fit.terms != terms:
            raise ValueError("All fits must have the same terms")

    if dfcom is None:
        dfcom = float(fits[0].df_residual)

    rows: list[dict[str, float | str]] = []
    for term in terms:
        q = np.array([fit.estimate[term] for fit in fits], dtype=np.float64)
        u = np.array([fit.variance[term] for fit in fits], dtype=np.float64)
        qbar = float(np.mean(q))
        ubar = float(np.mean(u))
        b = float(np.var(q, ddof=1))
        riv = (1.0 + 1.0 / m) * b / ubar if ubar > 0 else 0.0

        if rule == "rubin1987":
            t = ubar + (1.0 + 1.0 / m) * b
            df = barnard_rubin(m, b, t, dfcom)
            lam = (1.0 + 1.0 / m) * b / t if t > 0 else 0.0
            fmi = (riv + 2.0 / (df + 3.0)) / (riv + 1.0)
        elif rule == "reiter2003":
            t = ubar + b / m
            df = (m - 1.0) * (1.0 + (ubar / (b / m))) ** 2 if b > 0 else float("inf")
            lam = float("nan")
            fmi = float("nan")
        else:
            raise ValueError(f"Unknown pooling rule: {rule}")

        rows.append(
            {
                "term": term,
                "estimate": qbar,
                "std_error": float(np.sqrt(t)),
                "df": df,
                "riv": riv,
                "lambda": lam,
                "fmi": fmi,
            }
        )

    return PoolResult(m=m, rule=rule, dfcom=dfcom, rows=rows)


def summary_pool(
    pooled: PoolResult,
    alpha: float = 0.05,
) -> list[dict[str, float | str]]:
    """Summary table with test statistics and p-values (R ``summary.mipo``)."""
    out: list[dict[str, float | str]] = []
    for row in pooled.rows:
        est = float(row["estimate"])
        se = float(row["std_error"])
        df = float(row["df"])
        stat = est / se if se > 0 else float("nan")
        pval = float(2.0 * (1.0 - stats.t.cdf(abs(stat), df))) if se > 0 else float("nan")
        out.append(
            {
                "term": str(row["term"]),
                "estimate": est,
                "std_error": se,
                "statistic": stat,
                "df": df,
                "p_value": pval,
                "fmi": float(row["fmi"]),
            }
        )
    return out


def _pool_single(fit: FitResult) -> PoolResult:
    rows = [
        {
            "term": term,
            "estimate": fit.estimate[term],
            "std_error": float(np.sqrt(fit.variance[term])),
            "df": fit.df_residual,
            "riv": 0.0,
            "lambda": 0.0,
            "fmi": 0.0,
        }
        for term in fit.terms
    ]
    return PoolResult(m=1, rule="rubin1987", dfcom=fit.df_residual, rows=rows)


def anova(fit1: Mira, fit2: Mira) -> dict[str, object]:
    """Compare nested models pooled across multiple imputations (R ``anova.mira``)."""
    terms1 = set(fit1.analyses[0].terms)
    terms2 = set(fit2.analyses[0].terms)

    # Determine which model is nested (smaller) vs larger
    if terms1.issubset(terms2) and terms1 != terms2:
        _, larger = fit1, fit2
        s_terms, l_terms = terms1, terms2
    elif terms2.issubset(terms1) and terms1 != terms2:
        _, larger = fit2, fit1
        s_terms, l_terms = terms2, terms1
    else:
        raise ValueError("Models must be strictly nested to perform ANOVA comparison")

    extra_terms = sorted(list(l_terms - s_terms))
    pooled_larger = pool(larger)
    summary_larger = summary_pool(pooled_larger)

    t_stats = []
    dfs = []
    for row in summary_larger:
        if row["term"] in extra_terms:
            t_stats.append(float(row["statistic"]))
            dfs.append(float(row["df"]))

    q = len(extra_terms)
    f_stat = float(np.mean([t**2 for t in t_stats]))
    df_den = float(np.mean(dfs))
    pval = float(1.0 - stats.f.cdf(f_stat, q, df_den))

    print("Nested Model ANOVA Comparison:")
    print(f"  Smaller model terms: {sorted(list(s_terms))}")
    print(f"  Larger model terms:  {sorted(list(l_terms))}")
    print(f"  Extra terms:         {extra_terms}")
    print(f"  F-statistic:         {f_stat:.4f} on {q} and {df_den:.1f} df")
    print(f"  p-value:             {pval:.4e}")

    return {
        "F": f_stat,
        "df1": q,
        "df2": df_den,
        "p_value": pval,
        "extra_terms": extra_terms,
    }
