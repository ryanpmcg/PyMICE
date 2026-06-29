"""Diagnostic plots (requires matplotlib; optional ``[plot]`` extra)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from pymice.ampute import AmputeResult
from pymice.diagnostics.flux import FluxResult
from pymice.diagnostics.md_pattern import MdPatternResult
from pymice.types import Mids

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def _require_matplotlib():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "matplotlib is required for plotting. Install with: pip install pymice[plot]"
        ) from exc
    return plt


def plot_mids(
    mids: Mids,
    variables: list[str] | str | None = None,
    *,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Trace plot of chain means across iterations (R ``plot.mids``)."""
    plt = _require_matplotlib()

    if not mids.chain_mean:
        raise ValueError("no convergence diagnostics found on Mids object")

    if variables is None:
        varlist = [v for v in mids.column_names if v in mids.chain_mean]
    elif isinstance(variables, str):
        varlist = [variables]
    else:
        varlist = list(variables)

    varlist = [v for v in varlist if v in mids.chain_mean]
    if not varlist:
        raise ValueError("no plottable variables with convergence data")

    n_vars = len(varlist)
    own_figure = ax is None
    if own_figure:
        fig, axes = plt.subplots(n_vars, 1, figsize=(8, 2.5 * n_vars), squeeze=False)
        axes_list = [axes[i, 0] for i in range(n_vars)]
    else:
        fig = ax.figure
        axes_list = [ax]

    iterations = np.arange(1, mids.iteration + 1)
    for ax_i, name in zip(axes_list, varlist, strict=False):
        chains = mids.chain_mean[name]
        for j in range(mids.m):
            ax_i.plot(iterations, chains[:, j], marker="o", markersize=3, label=f"imp {j + 1}")
        ax_i.set_title(name)
        ax_i.set_xlabel("iteration")
        ax_i.set_ylabel("mean imputation")
        ax_i.legend(loc="best", fontsize=8)
        ax_i.grid(True, alpha=0.3)

    fig.tight_layout()
    return fig if own_figure else ax


def plot_md_pattern(
    result: MdPatternResult,
    *,
    rotate_names: bool = False,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Heatmap of missing-data patterns (R ``md.pattern`` plot)."""
    plt = _require_matplotlib()

    n_pat = result.matrix.shape[0] - 1
    n_col = result.matrix.shape[1] - 1
    body = result.matrix[:n_pat, :n_col]

    own_figure = ax is None
    if own_figure:
        fig, plot_ax = plt.subplots(figsize=(max(4, n_col), max(3, n_pat * 0.5)))
    else:
        fig = ax.figure
        plot_ax = ax

    plot_ax.imshow(body, aspect="auto", cmap="Blues", vmin=0, vmax=1)
    plot_ax.set_xticks(range(n_col))
    plot_ax.set_xticklabels(
        result.column_names,
        rotation=90 if rotate_names else 0,
        ha="right" if rotate_names else "center",
    )
    plot_ax.set_yticks(range(n_pat))
    plot_ax.set_yticklabels([str(c) for c in result.pattern_counts])
    plot_ax.set_xlabel("variable")
    plot_ax.set_ylabel("pattern count")
    plot_ax.set_title("Missing data pattern (1=observed)")

    for i in range(n_pat):
        for j in range(n_col):
            plot_ax.text(j, i, str(body[i, j]), ha="center", va="center", color="black", fontsize=9)

    fig.tight_layout()
    return fig if own_figure else plot_ax


def plot_raw_density(
    data: np.ndarray,
    variable: str,
    column_names: list[str],
    *,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Density of a single variable on incomplete data (R ``densityplot`` on vector)."""
    plt = _require_matplotlib()
    from scipy.stats import gaussian_kde

    j = column_names.index(variable)
    col = data[:, j]
    obs = col[np.isfinite(col)]

    own_figure = ax is None
    if own_figure:
        fig, plot_ax = plt.subplots(figsize=(6, 4))
    else:
        fig = ax.figure
        plot_ax = ax

    if obs.size > 1:
        kde = gaussian_kde(obs)
        xs = np.linspace(
            obs.min() - 0.2 * (obs.max() - obs.min()),
            obs.max() + 0.2 * (obs.max() - obs.min()),
            200,
        )
        ys = kde(xs)
        plot_ax.plot(xs, ys, color="C0", linewidth=2)
        # Rug plot at the bottom
        plot_ax.plot(obs, np.zeros_like(obs), "|", color="C0", markersize=6)

    plot_ax.set_xlabel(variable)
    plot_ax.set_ylabel("density")
    plot_ax.set_title(f"Density: {variable}")
    fig.tight_layout()
    return fig if own_figure else plot_ax


def plot_density(
    mids: Mids,
    variable: str,
    *,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Density of observed vs imputed values for one variable."""
    plt = _require_matplotlib()
    from scipy.stats import gaussian_kde

    if variable not in mids.column_names:
        raise ValueError(f"unknown variable: {variable}")

    j = mids.column_names.index(variable)
    observed = mids.data[:, j]
    obs_mask = np.isfinite(observed)
    obs_vals = observed[obs_mask]

    own_figure = ax is None
    if own_figure:
        fig, plot_ax = plt.subplots(figsize=(6, 4))
    else:
        fig = ax.figure
        plot_ax = ax

    if obs_vals.size > 1:
        kde_obs = gaussian_kde(obs_vals)
        xs = np.linspace(
            obs_vals.min() - 0.2 * (obs_vals.max() - obs_vals.min()),
            obs_vals.max() + 0.2 * (obs_vals.max() - obs_vals.min()),
            200,
        )
        plot_ax.plot(xs, kde_obs(xs), color="C0", linewidth=3, label="observed")
        plot_ax.plot(obs_vals, np.zeros_like(obs_vals), "|", color="C0", markersize=6)

    if variable in mids.imp:
        for k in range(mids.m):
            imp_vals = mids.imp[variable][:, k]
            imp_vals = imp_vals[np.isfinite(imp_vals)]
            if imp_vals.size > 1:
                try:
                    kde_imp = gaussian_kde(imp_vals)
                    plot_ax.plot(
                        xs,
                        kde_imp(xs),
                        color="C3",
                        linewidth=1,
                        alpha=0.6,
                        label="imputed" if k == 0 else "",
                    )
                except Exception:
                    pass

    plot_ax.set_xlabel(variable)
    plot_ax.set_ylabel("density")
    plot_ax.set_title(f"Observed vs imputed: {variable}")
    plot_ax.legend()
    fig.tight_layout()
    return fig if own_figure else plot_ax


def plot_density_by_imp(
    mids: Mids,
    variable: str,
    *,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Faceted density per imputation (R ``densityplot(imp, ~var | .imp)``)."""
    plt = _require_matplotlib()
    from scipy.stats import gaussian_kde

    if variable not in mids.column_names:
        raise ValueError(f"unknown variable: {variable}")

    own_figure = ax is None
    ncol = min(mids.m, 3)
    nrow = int(np.ceil(mids.m / ncol))
    if own_figure:
        fig, axes = plt.subplots(nrow, ncol, figsize=(3.5 * ncol, 2.5 * nrow), squeeze=False)
    else:
        fig = ax.figure
        axes = np.array([[ax]])

    j = mids.column_names.index(variable)
    obs = mids.data[:, j]
    obs_vals = obs[np.isfinite(obs)]

    for k in range(mids.m):
        r, c = divmod(k, ncol)
        plot_ax = axes[r, c]
        if obs_vals.size > 1:
            kde_obs = gaussian_kde(obs_vals)
            xs = np.linspace(
                obs_vals.min() - 0.2 * (obs_vals.max() - obs_vals.min()),
                obs_vals.max() + 0.2 * (obs_vals.max() - obs_vals.min()),
                200,
            )
            plot_ax.plot(xs, kde_obs(xs), color="C0", linewidth=1.5, label="obs")

        if variable in mids.imp:
            draw_vals = mids.imp[variable][:, k]
            draw_vals = draw_vals[np.isfinite(draw_vals)]
            if draw_vals.size > 1:
                try:
                    kde_imp = gaussian_kde(draw_vals)
                    plot_ax.plot(xs, kde_imp(xs), color="C3", linewidth=1.5, label="imp")
                except Exception:
                    pass
        plot_ax.set_title(f".imp = {k + 1}")
        plot_ax.set_xlabel(variable)
        if k == 0:
            plot_ax.legend(fontsize=7)

    for k in range(mids.m, nrow * ncol):
        r, c = divmod(k, ncol)
        axes[r, c].axis("off")

    fig.suptitle(f"Density by imputation: {variable}", y=1.02)
    fig.tight_layout()
    return fig if own_figure else ax


def plot_stripplot(
    mids: Mids,
    variable: str,
    *,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Imputed values by imputation draw (R ``stripplot(imp, var~.imp)``)."""
    plt = _require_matplotlib()
    if variable not in mids.imp:
        raise ValueError(f"no imputation storage for {variable}")

    own_figure = ax is None
    if own_figure:
        fig, plot_ax = plt.subplots(figsize=(7, 4))
    else:
        fig = ax.figure
        plot_ax = ax

    rng = np.random.default_rng(0)
    for k in range(mids.m):
        vals = mids.imp[variable][:, k]
        vals = vals[np.isfinite(vals)]
        if vals.size == 0:
            continue
        jitter = rng.uniform(-0.15, 0.15, size=vals.size)
        plot_ax.scatter(np.full(vals.size, k + 1) + jitter, vals, s=12, alpha=0.6)

    plot_ax.set_xlabel("imputation (.imp)")
    plot_ax.set_ylabel(variable)
    plot_ax.set_title(f"Stripplot: {variable}")
    plot_ax.set_xticks(range(1, mids.m + 1))
    fig.tight_layout()
    return fig if own_figure else ax


def plot_bwplot(
    mids: Mids,
    variable: str,
    *,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Boxplots of imputed values by draw (R ``bwplot(imp)``)."""
    plt = _require_matplotlib()
    if variable not in mids.imp:
        raise ValueError(f"no imputation storage for {variable}")

    own_figure = ax is None
    if own_figure:
        fig, plot_ax = plt.subplots(figsize=(7, 4))
    else:
        fig = ax.figure
        plot_ax = ax

    data = [mids.imp[variable][:, k][np.isfinite(mids.imp[variable][:, k])] for k in range(mids.m)]
    plot_ax.boxplot(data, tick_labels=[str(k + 1) for k in range(mids.m)])
    plot_ax.set_xlabel("imputation (.imp)")
    plot_ax.set_ylabel(variable)
    plot_ax.set_title(f"Boxplot by imputation: {variable}")
    fig.tight_layout()
    return fig if own_figure else ax


def plot_histogram(
    data: np.ndarray,
    column_names: list[str],
    variable: str,
    *,
    by: str | None = None,
    condition: NDArray[np.bool_] | None = None,
    n_bins: int = 25,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Histogram with optional conditioning (R ``histogram``)."""
    plt = _require_matplotlib()
    j = column_names.index(variable)
    col = data[:, j]
    valid = np.isfinite(col)

    own_figure = ax is None
    if by is not None or condition is not None:
        if own_figure:
            fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
        else:
            fig = ax.figure
            axes = [ax, ax]

        if condition is not None:
            masks = [condition & valid, (~condition) & valid]
            titles = ["condition TRUE", "condition FALSE"]
        else:
            by_j = column_names.index(by)
            by_col = data[:, by_j]
            med = np.nanmedian(by_col)
            masks = [(by_col <= med) & valid, (by_col > med) & valid]
            titles = [f"{by} low", f"{by} high"]

        for plot_ax, mask, title in zip(axes, masks, titles, strict=False):
            vals = col[mask]
            if vals.size:
                plot_ax.hist(vals, bins=n_bins, color="C0", edgecolor="white", alpha=0.8)
            plot_ax.set_title(f"{variable} | {title}")
            plot_ax.set_xlabel(variable)
        axes[0].set_ylabel("count")
    else:
        if own_figure:
            fig, plot_ax = plt.subplots(figsize=(6, 4))
        else:
            fig = ax.figure
            plot_ax = ax
        vals = col[valid]
        if vals.size:
            plot_ax.hist(vals, bins=n_bins, color="C0", edgecolor="white", alpha=0.8)
        plot_ax.set_xlabel(variable)
        plot_ax.set_ylabel("count")
        plot_ax.set_title(f"Histogram: {variable}")

    fig.tight_layout()
    return fig if own_figure else ax


def plot_xy_imputed(
    mids: Mids,
    y_var: str,
    x_values: np.ndarray,
    *,
    draw: int = 1,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Scatter of y vs x with imputed points highlighted (R ``xyplot``)."""
    from pymice.complete import complete

    plt = _require_matplotlib()
    y_j = mids.column_names.index(y_var)
    y = complete(mids, draw)[:, y_j]
    missing_y = np.isnan(mids.data[:, y_j])

    own_figure = ax is None
    if own_figure:
        fig, plot_ax = plt.subplots(figsize=(6, 5))
    else:
        fig = ax.figure
        plot_ax = ax

    obs = ~missing_y
    plot_ax.scatter(x_values[obs], y[obs], c="C0", s=20, alpha=0.7, label="observed")
    if np.any(missing_y):
        plot_ax.scatter(
            x_values[missing_y], y[missing_y], c="C3", s=30, marker="x", label="imputed"
        )

    plot_ax.set_xlabel("x")
    plot_ax.set_ylabel(y_var)
    plot_ax.set_title(f"{y_var} vs x (draw {draw})")
    plot_ax.legend()
    fig.tight_layout()
    return fig if own_figure else ax


def plot_xy_by_imp(
    mids: Mids,
    y_var: str,
    x_var: str,
    *,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Scatter faceted by imputation (R ``xyplot(imp, y ~ x | .imp)``)."""
    from pymice.complete import complete

    plt = _require_matplotlib()
    y_j = mids.column_names.index(y_var)
    x_j = mids.column_names.index(x_var)

    own_figure = ax is None
    ncol = min(mids.m, 3)
    nrow = int(np.ceil(mids.m / ncol))
    if own_figure:
        fig, axes = plt.subplots(nrow, ncol, figsize=(3.5 * ncol, 3 * nrow), squeeze=False)
    else:
        fig = ax.figure
        axes = np.array([[ax]])

    for k in range(mids.m):
        r, c = divmod(k, ncol)
        plot_ax = axes[r, c]
        filled = complete(mids, k + 1)
        x = filled[:, x_j]
        y = filled[:, y_j]
        valid = np.isfinite(x) & np.isfinite(y)
        plot_ax.scatter(x[valid], y[valid], s=10, alpha=0.6)
        plot_ax.set_title(f".imp = {k + 1}")
        plot_ax.set_xlabel(x_var)
        plot_ax.set_ylabel(y_var)

    for k in range(mids.m, nrow * ncol):
        r, c = divmod(k, ncol)
        axes[r, c].axis("off")

    fig.suptitle(f"{y_var} ~ {x_var} by imputation", y=1.02)
    fig.tight_layout()
    return fig if own_figure else ax


def plot_flux(
    result: FluxResult,
    *,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Bar chart of flux diagnostics (companion to R ``fluxplot`` table)."""
    plt = _require_matplotlib()
    own_figure = ax is None
    if own_figure:
        fig, plot_ax = plt.subplots(figsize=(10, 5))
    else:
        fig = ax.figure
        plot_ax = ax

    x = np.arange(len(result.column_names))
    width = 0.25
    plot_ax.bar(x - width, result.pobs, width, label="pobs")
    plot_ax.bar(x, result.influx, width, label="influx")
    plot_ax.bar(x + width, result.outflux, width, label="outflux")
    plot_ax.set_xticks(x)
    plot_ax.set_xticklabels(result.column_names, rotation=45, ha="right")
    plot_ax.set_ylabel("proportion")
    plot_ax.set_title("Flux diagnostics")
    plot_ax.legend()
    plot_ax.set_ylim(0, 1.05)
    fig.tight_layout()
    return fig if own_figure else ax


def plot_ampute_bwplot(
    result: AmputeResult,
    column_names: list[str],
    *,
    which_pat: int = 0,
    descriptives: bool = True,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Boxplots by amputation pattern (R ``bwplot(result, which.pat)``)."""
    plt = _require_matplotlib()
    amp = result.amp
    missing = np.isnan(amp)
    pat = result.patterns[which_pat].astype(bool)
    in_pat = np.all(missing[:, pat] == pat, axis=1) & np.all(~missing[:, ~pat], axis=1)

    own_figure = ax is None
    n_cols = amp.shape[1]
    if own_figure:
        fig, plot_ax = plt.subplots(figsize=(max(6, n_cols), 4))
    else:
        fig = ax.figure
        plot_ax = ax

    if descriptives:
        labels = []
        groups = []
        for j in range(n_cols):
            for label, mask in (("in", in_pat), ("out", ~in_pat)):
                vals = amp[mask, j]
                vals = vals[np.isfinite(vals)]
                if vals.size:
                    groups.append(vals)
                    labels.append(f"{column_names[j]}\n{label}")
        if groups:
            plot_ax.boxplot(groups, tick_labels=labels)
        plot_ax.set_title(f"Ampute pattern {which_pat + 1} (descriptives)")
    else:
        groups = [amp[in_pat, j][np.isfinite(amp[in_pat, j])] for j in range(n_cols)]
        plot_ax.boxplot(groups, tick_labels=column_names)
        plot_ax.set_title(f"Ampute pattern {which_pat + 1}")

    plot_ax.set_ylabel("value")
    fig.tight_layout()
    return fig if own_figure else ax


def plot_ampute_xyplot(
    result: AmputeResult,
    column_names: list[str],
    *,
    which_pat: int = 0,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Amputed vs observed scatter (R ``xyplot(result, which.pat)``)."""
    plt = _require_matplotlib()
    amp = result.amp
    j = min(which_pat, amp.shape[1] - 1)
    missing = np.isnan(amp[:, j])

    own_figure = ax is None
    if own_figure:
        fig, plot_ax = plt.subplots(figsize=(6, 4))
    else:
        fig = ax.figure
        plot_ax = ax

    other = (j + 1) % amp.shape[1]
    x = amp[:, other]
    y = amp[:, j]
    plot_ax.scatter(x[~missing], y[~missing], c="C0", s=8, alpha=0.5, label="observed")
    plot_ax.scatter(x[missing], y[missing], c="C3", s=12, marker="x", label="amputed")
    plot_ax.set_xlabel(column_names[other])
    plot_ax.set_ylabel(column_names[j])
    plot_ax.set_title(f"Ampute pattern {which_pat + 1}")
    plot_ax.legend()
    fig.tight_layout()
    return fig if own_figure else ax


def plot_km_missing(
    time: np.ndarray,
    event: np.ndarray,
    group_missing: np.ndarray,
    *,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Kaplan-Meier curves by missingness group (R ``plot(survfit(...))``)."""
    plt = _require_matplotlib()

    def _km(t: np.ndarray, e: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        order = np.argsort(t)
        t, e = t[order], e[order]
        uniq = np.unique(t)
        surv = 1.0
        xs, ys = [0.0], [1.0]
        n_at_risk = len(t)
        for ti in uniq:
            at_t = t == ti
            d = int(np.sum(e[at_t]))
            if d and n_at_risk:
                surv *= 1.0 - d / n_at_risk
            xs.append(float(ti))
            ys.append(surv)
            n_at_risk -= int(np.sum(at_t))
        return np.array(xs), np.array(ys)

    own_figure = ax is None
    if own_figure:
        fig, plot_ax = plt.subplots(figsize=(7, 5))
    else:
        fig = ax.figure
        plot_ax = ax

    for mask, label, color in (
        (group_missing, "missing", "C3"),
        (~group_missing, "observed", "C0"),
    ):
        t = time[mask]
        e = event[mask]
        valid = np.isfinite(t) & np.isfinite(e)
        if np.sum(valid) < 2:
            continue
        xs, ys = _km(t[valid], e[valid])
        plot_ax.step(xs, ys, where="post", label=label, color=color, linewidth=1.5)

    plot_ax.set_xlabel("time")
    plot_ax.set_ylabel("survival probability")
    plot_ax.set_title("Kaplan-Meier by missingness")
    plot_ax.legend()
    plot_ax.set_ylim(0, 1.05)
    fig.tight_layout()
    return fig if own_figure else ax
