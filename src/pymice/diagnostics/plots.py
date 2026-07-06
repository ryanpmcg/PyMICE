"""Diagnostic plots (requires matplotlib; optional ``[plot]`` extra)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from pymice.ampute import AmputeResult
from pymice.diagnostics.flux import FluxResult
from pymice.diagnostics.md_pattern import MdPatternResult
from pymice.types import Mids, VariableKind

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


def _plot_mids_chains(
    ax_i: Axes,
    chains: NDArray[np.floating],
    *,
    mids_m: int,
    iterations: NDArray[np.integer],
    show_xlabel: bool,
) -> None:
    for j in range(mids_m):
        ax_i.plot(iterations, chains[:, j], marker="o", markersize=3)
    if show_xlabel:
        ax_i.set_xlabel("Iteration")
    ax_i.grid(True, alpha=0.3)


def _set_mids_row_header(ax_left: Axes, ax_right: Axes, variable: str) -> None:
    """R ``plot.mids`` row headers: mean | sd with variable name on the right."""
    ax_left.set_title("mean", loc="left", fontsize=9, fontweight="normal", pad=6)
    ax_right.set_title("sd", loc="left", fontsize=9, fontweight="normal", pad=6)
    ax_right.text(
        1.0,
        1.02,
        variable,
        transform=ax_right.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
    )


def plot_mids(
    mids: Mids,
    variables: list[str] | str | None = None,
    *,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Trace plot of chain means and SDs (R ``plot.mids`` mean | sd layout)."""
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
    iterations = np.arange(1, mids.iteration + 1)

    if own_figure:
        fig, axes = plt.subplots(
            n_vars,
            2,
            figsize=(9, 2.5 * n_vars),
            squeeze=False,
            sharex=True,
        )
        for i, name in enumerate(varlist):
            mean_chains = np.asarray(mids.chain_mean[name], dtype=np.float64)
            var_arr = mids.chain_var.get(name)
            if var_arr is None:
                raise ValueError(f"no chain variance for variable: {name}")
            sd_chains = np.sqrt(np.asarray(var_arr, dtype=np.float64))
            show_ticks = i == n_vars - 1
            _set_mids_row_header(axes[i, 0], axes[i, 1], name)
            _plot_mids_chains(
                axes[i, 0],
                mean_chains,
                mids_m=mids.m,
                iterations=iterations,
                show_xlabel=False,
            )
            _plot_mids_chains(
                axes[i, 1],
                sd_chains,
                mids_m=mids.m,
                iterations=iterations,
                show_xlabel=False,
            )
            if not show_ticks:
                axes[i, 0].tick_params(labelbottom=False)
                axes[i, 1].tick_params(labelbottom=False)
        fig.supxlabel("Iteration")
        fig.tight_layout()
        return fig

    fig = ax.figure
    name = varlist[0]
    mean_chains = np.asarray(mids.chain_mean[name], dtype=np.float64)
    ax.set_title("mean", loc="left", fontsize=9)
    _plot_mids_chains(
        ax,
        mean_chains,
        mids_m=mids.m,
        iterations=iterations,
        show_xlabel=True,
    )
    fig.tight_layout()
    return ax


def plot_md_pattern(
    result: MdPatternResult,
    *,
    rotate_names: bool = False,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Missing-data pattern grid (R ``md.pattern(..., plot=TRUE)`` layout)."""
    from matplotlib.patches import Rectangle

    from pymice.diagnostics.theme import mdc

    plt = _require_matplotlib()

    n_pat = result.n_patterns
    n_col = len(result.column_names)
    body = result.matrix[:n_pat, :n_col]
    row_missings = result.matrix[:n_pat, -1]
    col_totals = result.matrix[-1, :n_col]
    grand_total = int(result.matrix[-1, -1])

    color_obs = mdc(1)
    color_miss = mdc(2)

    own_figure = ax is None
    if own_figure:
        name_pad = max(len(name) for name in result.column_names) / 2.6 if rotate_names else 0.0
        fig, plot_ax = plt.subplots(
            figsize=(max(3.0, n_col + 2.0), max(3.0, n_pat + 1.5 + name_pad))
        )
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    else:
        fig = ax.figure
        plot_ax = ax

    name_pad = max(len(name) for name in result.column_names) / 2.6 if rotate_names else 1.0
    plot_ax.set_xlim(-1, n_col + 1)
    plot_ax.set_ylim(-1, n_pat + name_pad)
    plot_ax.set_aspect("equal", adjustable="box")
    plot_ax.axis("off")

    for display_i in range(n_pat):
        pat_i = display_i
        y = n_pat - 1 - display_i
        for j in range(n_col):
            observed = int(body[pat_i, j]) == 1
            plot_ax.add_patch(
                Rectangle(
                    (j, y),
                    1,
                    1,
                    facecolor=color_obs if observed else color_miss,
                    edgecolor="black",
                    linewidth=0.6,
                )
            )

        plot_ax.text(
            -0.3,
            y + 0.5,
            str(result.pattern_counts[pat_i]),
            ha="right",
            va="center",
            fontsize=10,
        )
        plot_ax.text(
            n_col + 0.3,
            y + 0.5,
            str(int(row_missings[pat_i])),
            ha="left",
            va="center",
            fontsize=10,
        )

    for j, name in enumerate(result.column_names):
        if rotate_names:
            plot_ax.text(
                j + 0.5,
                n_pat + 0.3,
                name,
                ha="center",
                va="bottom",
                rotation=90,
                fontsize=10,
            )
        else:
            plot_ax.text(
                j + 0.5,
                n_pat + 0.3,
                name,
                ha="center",
                va="bottom",
                fontsize=10,
            )
        plot_ax.text(
            j + 0.5,
            -0.3,
            str(int(col_totals[j])),
            ha="center",
            va="top",
            fontsize=10,
        )

    plot_ax.text(
        n_col + 0.3,
        -0.3,
        str(grand_total),
        ha="left",
        va="top",
        fontsize=10,
    )

    return fig if own_figure else plot_ax


def plot_raw_density(
    data: np.ndarray,
    variable: str | None = None,
    column_names: list[str] | None = None,
    *,
    xlab: str | None = None,
    ylab: str = "Density",
    title: str | None = None,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    linewidth: float = 2.0,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Density of a single variable on incomplete data (R ``densityplot`` on vector)."""
    from scipy.stats import gaussian_kde

    from pymice.diagnostics.density_bw import density_limits, nrd0_kde_factor
    from pymice.diagnostics.theme import mdc

    plt = _require_matplotlib()

    if data.ndim == 1:
        obs = data[np.isfinite(data)]
        x_label = xlab or variable or "x"
    else:
        if variable is None or column_names is None:
            raise ValueError("variable and column_names are required for 2-D data")
        j = column_names.index(variable)
        obs = data[:, j]
        obs = obs[np.isfinite(obs)]
        x_label = xlab or variable

    line_color = mdc(4)

    own_figure = ax is None
    if own_figure:
        fig, plot_ax = plt.subplots(figsize=(6, 4))
    else:
        fig = ax.figure
        plot_ax = ax

    if obs.size > 1:
        kde = gaussian_kde(obs, bw_method=nrd0_kde_factor)
        x_from, x_to = density_limits(obs)
        if xlim is None:
            xlim = (x_from, x_to)
        xs = np.linspace(x_from, x_to, 512)
        ys = kde(xs)
        plot_ax.plot(xs, ys, color=line_color, linewidth=linewidth)
        plot_ax.plot(
            obs,
            np.zeros_like(obs),
            linestyle="none",
            marker="o",
            markerfacecolor="none",
            markeredgecolor=line_color,
            markeredgewidth=0.8,
            markersize=4,
        )

    plot_ax.set_xlabel(x_label)
    plot_ax.set_ylabel(ylab)
    if title is not None:
        plot_ax.set_title(title)
    if xlim is not None:
        plot_ax.set_xlim(xlim)
    if ylim is not None:
        plot_ax.set_ylim(ylim)
    fig.tight_layout()
    return fig if own_figure else plot_ax


def _density_grid_variables(mids: Mids) -> list[str]:
    """Variables included in R ``densityplot(imp)`` without a formula."""
    n_obs = mids.n_obs
    out: list[str] = []
    for name in mids.column_names:
        if name not in mids.imp or not mids.method.get(name, ""):
            continue
        nmis = mids.nmis.get(name, 0)
        if nmis <= 2 or nmis >= n_obs - 1:
            continue
        spec = next((s for s in mids.variable_specs if s.name == name), None)
        if spec is not None and spec.kind != VariableKind.NUMERIC:
            continue
        if mids.method.get(name, "") in ("logreg", "polyreg", "polr", "mlogreg"):
            continue
        out.append(name)
    return out


def _density_xgrid(
    obs_vals: NDArray[np.floating], imp_draws: list[NDArray[np.floating]]
) -> NDArray[np.floating]:
    parts = [obs_vals] if obs_vals.size else []
    for draw in imp_draws:
        finite = draw[np.isfinite(draw)]
        if finite.size:
            parts.append(finite)
    if not parts:
        return np.linspace(0.0, 1.0, 200)
    all_vals = np.concatenate(parts)
    if all_vals.size < 2:
        return np.linspace(all_vals.min() - 1.0, all_vals.max() + 1.0, 200)
    span = float(all_vals.max() - all_vals.min())
    pad = 0.2 * span if span > 0 else 1.0
    return np.linspace(all_vals.min() - pad, all_vals.max() + pad, 200)


def _plot_density_panel(
    plot_ax: Axes,
    mids: Mids,
    variable: str,
    *,
    title: str | None = None,
    xlab: str | None = None,
    ylab: str | None = None,
    show_legend: bool = True,
    linewidth_obs: float = 3.0,
    linewidth_imp: float = 1.0,
    imp_alpha: float = 0.6,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
) -> None:
    from scipy.stats import gaussian_kde

    if variable not in mids.column_names:
        raise ValueError(f"unknown variable: {variable}")

    j = mids.column_names.index(variable)
    observed = mids.data[:, j]
    obs_vals = observed[np.isfinite(observed)]

    imp_draws: list[NDArray[np.floating]] = []
    if variable in mids.imp:
        for k in range(mids.m):
            draw = mids.imp[variable][:, k]
            imp_draws.append(draw[np.isfinite(draw)])

    xs = _density_xgrid(obs_vals, imp_draws)

    if obs_vals.size > 1:
        kde_obs = gaussian_kde(obs_vals)
        plot_ax.plot(xs, kde_obs(xs), color="C0", linewidth=linewidth_obs, label="observed")
        plot_ax.plot(obs_vals, np.zeros_like(obs_vals), "|", color="C0", markersize=6)

    if variable in mids.imp:
        for k, imp_vals in enumerate(imp_draws):
            if imp_vals.size > 1:
                try:
                    kde_imp = gaussian_kde(imp_vals)
                    plot_ax.plot(
                        xs,
                        kde_imp(xs),
                        color="C3",
                        linewidth=linewidth_imp,
                        alpha=imp_alpha,
                        label="imputed" if k == 0 else "",
                    )
                except Exception:
                    pass

    if xlab is not None:
        plot_ax.set_xlabel(xlab)
    if ylab is not None:
        plot_ax.set_ylabel(ylab)
    if title is not None:
        plot_ax.set_title(title)
    if xlim is not None:
        plot_ax.set_xlim(xlim)
    if ylim is not None:
        plot_ax.set_ylim(ylim)
    if show_legend:
        plot_ax.legend()


def plot_density(
    mids: Mids,
    variable: str,
    *,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Density of observed vs imputed values for one variable."""
    plt = _require_matplotlib()

    own_figure = ax is None
    if own_figure:
        fig, plot_ax = plt.subplots(figsize=(6, 4))
    else:
        fig = ax.figure
        plot_ax = ax

    _plot_density_panel(
        plot_ax,
        mids,
        variable,
        xlab=variable,
        ylab="density",
        title=f"Observed vs imputed: {variable}",
        show_legend=True,
        xlim=xlim,
        ylim=ylim,
    )
    if own_figure:
        fig.tight_layout()
    return fig if own_figure else plot_ax


def plot_density_kde_lines(
    series: dict[str, NDArray[np.floating]],
    *,
    xlab: str = "",
    title: str = "",
    colors: dict[str, str] | None = None,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    linewidth: float = 2.0,
) -> Figure:
    """Overlay KDE curves (R ``plot(density(x)); lines(density(y), col=...)``)."""
    from scipy.stats import gaussian_kde

    plt = _require_matplotlib()
    fig, plot_ax = plt.subplots(figsize=(6, 4))
    palette = colors or {}
    all_vals = np.concatenate([vals[np.isfinite(vals)] for vals in series.values() if vals.size])
    if all_vals.size < 2:
        raise ValueError("need at least two finite values to plot densities")
    xmin = float(np.min(all_vals))
    xmax = float(np.max(all_vals))
    pad = 0.05 * (xmax - xmin) if xmax > xmin else 1.0
    xs = np.linspace(xmin - pad, xmax + pad, 200)
    for label, vals in series.items():
        finite = vals[np.isfinite(vals)]
        if finite.size < 2:
            continue
        kde = gaussian_kde(finite)
        plot_ax.plot(
            xs,
            kde(xs),
            color=palette.get(label, "C0"),
            linewidth=linewidth,
            label=label,
        )
    if xlab:
        plot_ax.set_xlabel(xlab)
    plot_ax.set_ylabel("Density")
    if title:
        plot_ax.set_title(title)
    if xlim is not None:
        plot_ax.set_xlim(xlim)
    if ylim is not None:
        plot_ax.set_ylim(ylim)
    fig.tight_layout()
    return fig


def plot_density_grid(
    mids: Mids,
    variables: list[str] | None = None,
    *,
    ncol: int = 2,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Faceted observed vs imputed densities (R ``densityplot(imp)``)."""
    plt = _require_matplotlib()

    varlist = _density_grid_variables(mids) if variables is None else list(variables)
    if not varlist:
        raise ValueError("no plottable imputed variables for density grid")

    n_vars = len(varlist)
    nrow = int(np.ceil(n_vars / ncol))
    own_figure = ax is None
    if own_figure:
        fig, axes = plt.subplots(
            nrow,
            ncol,
            figsize=(3.5 * ncol, 2.5 * nrow),
            squeeze=False,
        )
    else:
        fig = ax.figure
        axes = np.array([[ax]])

    for i, name in enumerate(varlist):
        r, c = divmod(i, ncol)
        panel_ax = axes[r, c]
        _plot_density_panel(
            panel_ax,
            mids,
            name,
            title=name,
            ylab="Density" if c == 0 else None,
            show_legend=False,
        )

    for k in range(n_vars, nrow * ncol):
        r, c = divmod(k, ncol)
        axes[r, c].axis("off")

    if own_figure:
        fig.tight_layout()
    return fig if own_figure else ax


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


def _bwplot_grid_variables(mids: Mids) -> list[str]:
    """Variables included in R ``bwplot(imp)`` without a formula."""
    out: list[str] = []
    for name in mids.column_names:
        spec = next((s for s in mids.variable_specs if s.name == name), None)
        if spec is not None and spec.kind in (VariableKind.UNORDERED, VariableKind.ORDERED):
            continue
        out.append(name)
    return out


def _plot_bwplot_panel(
    plot_ax: Axes,
    mids: Mids,
    variable: str,
    *,
    title: str | None = None,
    xlab: str | None = None,
    ylab: str | None = None,
) -> None:
    if variable not in mids.column_names:
        raise ValueError(f"unknown variable: {variable}")

    j = mids.column_names.index(variable)
    observed = mids.data[:, j]
    obs_vals = observed[np.isfinite(observed)]

    imp_draws: list[NDArray[np.floating]] = []
    if variable in mids.imp:
        for k in range(mids.m):
            draw = mids.imp[variable][:, k]
            imp_draws.append(draw[np.isfinite(draw)])
    else:
        imp_draws = [np.array([], dtype=np.float64) for _ in range(mids.m)]

    boxes = [obs_vals, *imp_draws]
    positions = list(range(mids.m + 1))
    labels = ["0", *[str(k + 1) for k in range(mids.m)]]
    bp = plot_ax.boxplot(
        boxes,
        positions=positions,
        widths=0.6,
        patch_artist=True,
        tick_labels=labels,
    )
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor("C0" if i == 0 else "C3")
        patch.set_alpha(0.55 if i == 0 else 0.35)

    if title is not None:
        plot_ax.set_title(title)
    if xlab is not None:
        plot_ax.set_xlabel(xlab)
    if ylab is not None:
        plot_ax.set_ylabel(ylab)


def plot_bwplot(
    mids: Mids,
    variable: str,
    *,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Boxplots of observed vs imputed values by draw (R ``bwplot(imp, var)``)."""
    plt = _require_matplotlib()

    own_figure = ax is None
    if own_figure:
        fig, plot_ax = plt.subplots(figsize=(7, 4))
    else:
        fig = ax.figure
        plot_ax = ax

    _plot_bwplot_panel(
        plot_ax,
        mids,
        variable,
        xlab="Imputation number",
        ylab=variable,
        title=f"Boxplot by imputation: {variable}",
    )
    if own_figure:
        fig.tight_layout()
    return fig if own_figure else plot_ax


def plot_bwplot_grid(
    mids: Mids,
    variables: list[str] | None = None,
    *,
    ncol: int = 4,
    ax: Axes | None = None,
) -> Figure | Axes:
    """Faceted observed vs imputed boxplots (R ``bwplot(imp)``)."""
    plt = _require_matplotlib()

    varlist = _bwplot_grid_variables(mids) if variables is None else list(variables)
    if not varlist:
        raise ValueError("no plottable variables for bwplot grid")

    n_vars = len(varlist)
    nrow = int(np.ceil(n_vars / ncol))
    own_figure = ax is None
    if own_figure:
        fig, axes = plt.subplots(
            nrow,
            ncol,
            figsize=(2.5 * ncol, 2.2 * nrow),
            squeeze=False,
        )
    else:
        fig = ax.figure
        axes = np.array([[ax]])

    for i, name in enumerate(varlist):
        r, c = divmod(i, ncol)
        panel_ax = axes[r, c]
        _plot_bwplot_panel(
            panel_ax,
            mids,
            name,
            title=name,
            ylab=name if ncol == 1 else None,
        )
        if r < nrow - 1:
            panel_ax.set_xlabel("")
            panel_ax.tick_params(labelbottom=False)

    for k in range(n_vars, nrow * ncol):
        r, c = divmod(k, ncol)
        axes[r, c].axis("off")

    if own_figure:
        fig.supxlabel("Imputation number")
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
            fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
        else:
            fig = ax.figure
            axes = [ax, ax]

        if condition is not None:
            masks = [(~condition) & valid, condition & valid]
            titles = ["FALSE", "TRUE"]
        else:
            by_j = column_names.index(by)
            by_col = data[:, by_j]
            med = np.nanmedian(by_col)
            masks = [(by_col <= med) & valid, (by_col > med) & valid]
            titles = [f"{by} low", f"{by} high"]

        vals_all = col[valid]
        if vals_all.size:
            xmin = float(np.min(vals_all))
            xmax = float(np.max(vals_all))
            pad = 0.05 * (xmax - xmin) if xmax > xmin else 1.0
            xlim = (xmin - pad, xmax + pad)
        else:
            xlim = None

        for plot_ax, mask, title in zip(axes, masks, titles, strict=False):
            vals = col[mask]
            if vals.size:
                plot_ax.hist(
                    vals,
                    bins=n_bins,
                    color="C0",
                    edgecolor="white",
                    alpha=0.8,
                    weights=np.full(vals.size, 100.0 / vals.size),
                )
            plot_ax.set_title(title)
            if xlim is not None:
                plot_ax.set_xlim(xlim)
        axes[0].set_ylabel("Percent of Total")
        fig.supxlabel(variable)
    else:
        if own_figure:
            fig, plot_ax = plt.subplots(figsize=(6, 4))
        else:
            fig = ax.figure
            plot_ax = ax
        vals = col[valid]
        if vals.size:
            uniq = np.unique(vals)
            if uniq.size <= 10 and np.allclose(uniq, np.round(uniq)):
                bins = np.arange(uniq.min() - 0.5, uniq.max() + 1.5, 1.0)
            else:
                bins = n_bins
            plot_ax.hist(
                vals,
                bins=bins,
                color="C0",
                edgecolor="white",
                alpha=0.8,
                weights=np.full(vals.size, 100.0 / vals.size),
            )
        plot_ax.set_xlabel(variable)
        plot_ax.set_ylabel("Percent of Total")
        plot_ax.set_title(f"Histogram: {variable}")

    fig.tight_layout()
    return fig if own_figure else ax


def plot_histogram_facets(
    series: dict[str, NDArray[np.floating]],
    *,
    variable: str,
    facet_order: list[str] | None = None,
    n_bins: int = 25,
) -> Figure:
    """Faceted percent histograms (R ``histogram(~ x | group)``)."""
    plt = _require_matplotlib()
    labels = facet_order or sorted(series)
    fig, axes = plt.subplots(1, len(labels), figsize=(5 * len(labels), 4), sharex=True, sharey=True)
    if len(labels) == 1:
        axes = [axes]

    all_vals = np.concatenate([series[label][np.isfinite(series[label])] for label in labels])
    if all_vals.size:
        rounded = np.round(all_vals)
        if np.allclose(all_vals, rounded):
            xmin = float(np.min(rounded))
            xmax = float(np.max(rounded))
            bins = np.arange(xmin - 0.5, xmax + 1.5, 1.0)
            xlim = (xmin - 0.5, xmax + 0.5)
        else:
            xmin = float(np.min(all_vals))
            xmax = float(np.max(all_vals))
            pad = 0.05 * (xmax - xmin) if xmax > xmin else 1.0
            bins = n_bins
            xlim = (xmin - pad, xmax + pad)
    else:
        bins = n_bins
        xlim = None

    for plot_ax, label in zip(axes, labels, strict=True):
        vals = series[label]
        vals = vals[np.isfinite(vals)]
        if vals.size:
            plot_ax.hist(
                vals,
                bins=bins,
                color="C0",
                edgecolor="white",
                alpha=0.8,
                weights=np.full(vals.size, 100.0 / vals.size),
            )
        plot_ax.set_title(label)
        if xlim is not None:
            plot_ax.set_xlim(xlim)
    axes[0].set_ylabel("Percent of Total")
    fig.supxlabel(variable)
    fig.tight_layout()
    return fig


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
    obs_cols = result.patterns[which_pat] == 1
    miss_cols = result.patterns[which_pat] == 0
    in_pat = np.all(~missing[:, obs_cols], axis=1) & np.all(missing[:, miss_cols], axis=1)

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
