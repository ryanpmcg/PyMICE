"""Multivariate model comparison and pooling statistics (D1, D2, D3)."""

from __future__ import annotations

import numpy as np
from scipy import stats

from pymice.pool.pool import anova
from pymice.types import Mira


def D1(fit1: Mira, fit2: Mira) -> dict[str, object]:
    """Calculate the D1 statistic (pooled multivariate Wald test, R ``D1``)."""
    return anova(fit1, fit2)


def D2(fit1: Mira, fit2: Mira) -> dict[str, object]:
    """Calculate the D2 statistic (pooling individual Wald/F-statistics, R ``D2``)."""
    terms1 = set(fit1.analyses[0].terms)
    terms2 = set(fit2.analyses[0].terms)

    if terms1.issubset(terms2) and terms1 != terms2:
        smaller, larger = fit1, fit2
        s_terms, l_terms = terms1, terms2
    elif terms2.issubset(terms1) and terms1 != terms2:
        smaller, larger = fit2, fit1
        s_terms, l_terms = terms2, terms1
    else:
        raise ValueError("Models must be strictly nested to calculate D2")

    m = smaller.m
    extra_terms = l_terms - s_terms
    q = len(extra_terms)

    # Compute individual F-statistics (or Wald statistics)
    d = []
    for i in range(m):
        fit_s = smaller.analyses[i]
        fit_l = larger.analyses[i]
        rss_s = getattr(fit_s, "rss", None)
        rss_l = getattr(fit_l, "rss", None)

        if rss_s is None or rss_l is None:
            # Fallback: average squared t-statistics for this imputation
            t_stats = [
                fit_l.estimate[t] / np.sqrt(fit_l.variance[t])
                for t in fit_l.terms
                if t in extra_terms
            ]
            d_i = float(np.mean([t**2 for t in t_stats]))
        else:
            d_i = (
                ((rss_s - rss_l) / q) / (rss_l / fit_l.df_residual)
                if rss_l > 0
                else 0.0
            )
        d.append(d_i)

    d_arr = np.array(d, dtype=np.float64)
    dbar = float(np.mean(d_arr))
    var_d = float(np.var(d_arr, ddof=1)) if m > 1 else 0.0

    r2 = (1.0 + 1.0 / m) * var_d / 2.0 if m > 1 else 0.0
    f_stat = dbar / (1.0 + r2) if (1.0 + r2) > 0 else 0.0

    if m > 1 and r2 > 0:
        df2 = q * (m - 1) * (1.0 + 1.0 / r2) ** 2
        pval = float(1.0 - stats.f.cdf(f_stat, q, df2))
    else:
        df2 = float("inf")
        pval = float(stats.chi2.sf(f_stat * q, q))

    return {
        "F": f_stat,
        "df1": q,
        "df2": df2,
        "p_value": pval,
        "r2": r2,
    }


def D3(fit1: Mira, fit2: Mira) -> dict[str, object]:
    """Calculate the D3 statistic (pooled likelihood ratio test, R ``D3``)."""
    terms1 = set(fit1.analyses[0].terms)
    terms2 = set(fit2.analyses[0].terms)

    if terms1.issubset(terms2) and terms1 != terms2:
        smaller, larger = fit1, fit2
        s_terms, l_terms = terms1, terms2
    elif terms2.issubset(terms1) and terms1 != terms2:
        smaller, larger = fit2, fit1
        s_terms, l_terms = terms2, terms1
    else:
        raise ValueError("Models must be strictly nested to calculate D3")

    m = smaller.m
    extra_terms = l_terms - s_terms
    q = len(extra_terms)

    d = []
    for i in range(m):
        fit_s = smaller.analyses[i]
        fit_l = larger.analyses[i]
        rss_s = getattr(fit_s, "rss", None)
        rss_l = getattr(fit_l, "rss", None)

        if rss_s is not None and rss_l is not None:
            # LRT for OLS/deviance: n_obs * log(rss_s / rss_l)
            # If rss is deviance (GLM), the difference is dev_s - dev_l
            if rss_s > rss_l * 1.5:  # likely OLS RSS
                n = fit_l.n_obs
                d_i = n * np.log(rss_s / rss_l) if rss_l > 0 else 0.0
            else:  # likely deviance differences
                d_i = rss_s - rss_l
        else:
            t_stats = [
                fit_l.estimate[t] / np.sqrt(fit_l.variance[t])
                for t in fit_l.terms
                if t in extra_terms
            ]
            d_i = float(np.sum([t**2 for t in t_stats]))
        d.append(d_i)

    d_arr = np.array(d, dtype=np.float64)
    dbar = float(np.mean(d_arr))

    pval = float(1.0 - stats.chi2.cdf(dbar, q))

    return {
        "statistic": dbar,
        "df": q,
        "p_value": pval,
    }
