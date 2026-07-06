"""R ``mice``-style plot dispatch over matplotlib diagnostics."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import numpy as np

from pymice.ampute import AmputeResult
from pymice.data_input import prepare_tabular_input
from pymice.diagnostics.flux import FluxResult, flux
from pymice.diagnostics.plots import (
    plot_ampute_bwplot,
    plot_bwplot,
    plot_bwplot_grid,
    plot_density,
    plot_density_by_imp,
    plot_density_grid,
    plot_flux,
    plot_mids,
    plot_raw_density,
    plot_stripplot,
    plot_xy_by_imp,
    plot_xy_imputed,
)
from pymice.types import Mids

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

_I_EXPR_RE = re.compile(r"^I\((.+)\)$", re.IGNORECASE)


def _parse_formula_parts(formula: str) -> tuple[str, str, str | None]:
    """Split ``y ~ x | facet`` into lhs, rhs, and optional facet."""
    text = formula.strip()
    facet: str | None = None
    if "|" in text:
        text, facet = (part.strip() for part in text.split("|", 1))

    if text.startswith("~"):
        lhs, rhs = "", text[1:].strip()
    elif "~" in text:
        lhs, rhs = (part.strip() for part in text.split("~", 1))
    else:
        raise ValueError(f"formula must contain '~': {formula!r}")

    return lhs, rhs, facet


def _eval_I_expression(expr: str, mids: Mids, *, draw: int = 1) -> np.ndarray:
    """Evaluate a simple ``I(...)`` expression on a completed dataset."""
    from pymice.complete import complete

    filled = complete(mids, draw, as_dataframe=False)
    namespace: dict[str, np.ndarray] = {}
    for name in mids.column_names:
        j = mids.column_names.index(name)
        namespace[name] = filled[:, j]
    namespace.update({"np": np, "nan": np.nan})
    try:
        return np.asarray(eval(expr, {"__builtins__": {}}, namespace), dtype=np.float64)
    except Exception as exc:
        raise ValueError(f"could not evaluate I({expr}): {exc}") from exc


def _resolve_xy_terms(
    mids: Mids,
    formula: str,
) -> tuple[str, np.ndarray | str]:
    """Return response name and x values (array or column name) for xy plots."""
    y_name, x_term, _ = _parse_formula_parts(formula)
    if not y_name:
        raise ValueError("xyplot formula requires a response on the left of '~'")

    if _I_EXPR_RE.match(x_term):
        expr = _I_EXPR_RE.match(x_term).group(1).strip()
        return y_name, _eval_I_expression(expr, mids)
    if x_term not in mids.column_names:
        raise ValueError(f"unknown predictor in formula: {x_term!r}")
    return y_name, x_term


def plot(
    mids: Mids,
    variables: list[str] | str | None = None,
    *,
    ax: Axes | None = None,
    **kwargs: Any,
) -> Figure | Axes:
    """Trace plot of chain means and SDs (R ``plot.mids``)."""
    if kwargs:
        raise TypeError(f"plot() got unexpected keyword arguments: {sorted(kwargs)}")
    return plot_mids(mids, variables=variables, ax=ax)


def _densityplot_raw_kwargs(
    *,
    xlab: str | None = None,
    ylab: str = "Density",
    title: str | None = None,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    linewidth: float = 2.0,
    ax: Axes | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    allowed = {
        "xlab",
        "ylab",
        "title",
        "xlim",
        "ylim",
        "linewidth",
        "ax",
    }
    extra = set(kwargs) - allowed
    if extra:
        raise TypeError(f"densityplot() got unexpected keyword arguments: {sorted(extra)}")
    return {
        "xlab": xlab,
        "ylab": ylab,
        "title": title,
        "xlim": xlim,
        "ylim": ylim,
        "linewidth": linewidth,
        "ax": ax,
    }


def densityplot(
    obj: Mids | np.ndarray | Any,
    formula: str | None = None,
    *,
    column_names: list[str] | None = None,
    xlab: str | None = None,
    ylab: str = "Density",
    title: str | None = None,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    linewidth: float = 2.0,
    ax: Axes | None = None,
    **kwargs: Any,
) -> Figure | Axes:
    """
    Density diagnostics (R ``densityplot``).

    Examples
    --------
    >>> densityplot(imp)
    >>> densityplot(imp, "~ bmi")
    >>> densityplot(imp, "~ bmi | .imp")
    >>> densityplot(nhanes["bmi"], xlab="nhanes$bmi")
    """
    raw_kw = _densityplot_raw_kwargs(
        xlab=xlab,
        ylab=ylab,
        title=title,
        xlim=xlim,
        ylim=ylim,
        linewidth=linewidth,
        ax=ax,
        **kwargs,
    )

    if isinstance(obj, Mids):
        if formula is None:
            return plot_density_grid(obj, ax=raw_kw["ax"])
        lhs, rhs, facet = _parse_formula_parts(formula)
        variable = rhs if not lhs else lhs
        if variable not in obj.column_names:
            raise ValueError(f"unknown variable: {variable!r}")
        if facet == ".imp":
            return plot_density_by_imp(obj, variable, ax=raw_kw["ax"])
        if facet is not None:
            raise ValueError(f"unsupported densityplot facet: {facet!r}")
        return plot_density(obj, variable, ax=raw_kw["ax"])

    from pymice.data_input import is_pandas_dataframe, is_pandas_series

    if is_pandas_series(obj):
        values = np.asarray(obj, dtype=np.float64)
        if raw_kw["xlab"] is None and getattr(obj, "name", None):
            raw_kw["xlab"] = f"nhanes${obj.name}"
        return plot_raw_density(values, **raw_kw)

    if is_pandas_dataframe(obj):
        raise TypeError(
            "densityplot() on a DataFrame requires a formula, e.g. densityplot(df, '~ bmi')"
        )

    if isinstance(obj, np.ndarray):
        if obj.ndim == 1:
            return plot_raw_density(obj, **raw_kw)
        if formula is None:
            raise TypeError("formula is required when densityplot() receives a 2-D ndarray")
        if column_names is None:
            raise TypeError("column_names is required when densityplot() receives a 2-D ndarray")
        lhs, rhs, facet = _parse_formula_parts(formula)
        variable = rhs if not lhs else lhs
        if facet is not None:
            raise ValueError("densityplot on raw data does not support '| .imp' faceting")
        return plot_raw_density(obj, variable, column_names, **raw_kw)

    raise TypeError("densityplot() requires a Mids object, ndarray, or pandas Series")


def stripplot(
    mids: Mids,
    formula: str,
    *,
    ax: Axes | None = None,
    **kwargs: Any,
) -> Figure | Axes:
    """Imputed values by draw (R ``stripplot(imp, y ~ .imp)``)."""
    if kwargs:
        raise TypeError(f"stripplot() got unexpected keyword arguments: {sorted(kwargs)}")

    y_name, rhs, facet = _parse_formula_parts(formula)
    if facet is not None and facet != ".imp":
        raise ValueError(f"unsupported stripplot facet: {facet!r}")
    if rhs != ".imp":
        raise ValueError("stripplot formula must be 'y ~ .imp'")
    if not y_name:
        raise ValueError("stripplot formula requires a variable on the left of '~'")
    return plot_stripplot(mids, y_name, ax=ax)


def xyplot(
    mids: Mids,
    formula: str,
    *,
    draw: int = 1,
    ax: Axes | None = None,
    **kwargs: Any,
) -> Figure | Axes:
    """
    Scatter of imputed data (R ``xyplot``).

    Supports ``y ~ x`` and simple ``y ~ I(expr)`` transforms.
    """
    if kwargs:
        raise TypeError(f"xyplot() got unexpected keyword arguments: {sorted(kwargs)}")

    y_name, x_term, facet = _parse_formula_parts(formula)
    if facet == ".imp":
        if not y_name:
            raise ValueError("xyplot facet formula requires 'y ~ x | .imp'")
        if isinstance(x_term, str) and x_term in mids.column_names:
            return plot_xy_by_imp(mids, y_name, x_term, ax=ax)
        raise ValueError("xyplot with '| .imp' requires a column name on the right of '~'")

    y_name, x_term = _resolve_xy_terms(mids, formula)
    if isinstance(x_term, str):
        x_j = mids.column_names.index(x_term)
        from pymice.complete import complete

        filled = complete(mids, draw, as_dataframe=False)
        x_values = filled[:, x_j]
    else:
        x_values = x_term
    return plot_xy_imputed(mids, y_name, x_values, draw=draw, ax=ax)


def bwplot(
    obj: Mids | AmputeResult,
    formula: str | None = None,
    *,
    variable: str | None = None,
    column_names: list[str] | None = None,
    ax: Axes | None = None,
    **kwargs: Any,
) -> Figure | Axes:
    """Boxplot diagnostics (R ``bwplot`` on mids or ampute result)."""
    if isinstance(obj, AmputeResult):
        if column_names is None:
            raise TypeError("column_names is required for bwplot(AmputeResult)")
        return plot_ampute_bwplot(obj, column_names, ax=ax)

    if kwargs:
        raise TypeError(f"bwplot() got unexpected keyword arguments: {sorted(kwargs)}")

    var = variable
    if formula is not None:
        y_name, rhs, facet = _parse_formula_parts(formula)
        if facet is not None and facet != ".imp":
            raise ValueError(f"unsupported bwplot facet: {facet!r}")
        if rhs != ".imp":
            raise ValueError("bwplot formula must be 'y ~ .imp'")
        var = y_name or var
    if not var:
        if formula is None:
            return plot_bwplot_grid(obj, ax=ax)
        imputed = [name for name in obj.column_names if name in obj.imp]
        if not imputed:
            raise ValueError("bwplot() requires formula or variable= for Mids")
        var = imputed[0]
    return plot_bwplot(obj, var, ax=ax)


def fluxplot(
    data: Any,
    *,
    column_names: list[str] | None = None,
    ax: Axes | None = None,
    return_table: bool = False,
    **kwargs: Any,
) -> Figure | Axes | tuple[FluxResult, Figure | Axes]:
    """
    Flux diagnostic plot (R ``fluxplot()``).

    Computes ``flux()`` on incomplete data and draws the bar chart. Pass
    ``return_table=True`` to also receive the ``FluxResult`` table.
    """
    if kwargs:
        raise TypeError(f"fluxplot() got unexpected keyword arguments: {sorted(kwargs)}")

    matrix, names = prepare_tabular_input(data, column_names)
    result = flux(matrix, names)
    fig = plot_flux(result, ax=ax)
    if return_table:
        return result, fig
    return fig
