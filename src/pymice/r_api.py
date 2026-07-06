"""R ``mice``-familiar top-level helpers (``with_``, ``summary``, ``mice_mids``, ``futuremice``)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pymice.analysis.glm import glm
from pymice.analysis.ols import lm
from pymice.continue_mids import continue_imputation
from pymice.parallel import parallel_mice
from pymice.pool.pool import summary_pool
from pymice.r_compat import normalize_mice_kwargs, resolve_print_flag
from pymice.types import FitResult, Mira, PoolResult
from pymice.with_mids import with_mids


def with_(
    data: Any,
    expr: Callable[..., FitResult] | str,
    formula: str | None = None,
    *,
    family: str | None = None,
) -> Mira:
    """
    Evaluate an expression on each imputed dataset (R ``with.mids``).

    Examples
    --------
    >>> with_(imp, "bmi ~ age")
    >>> with_(imp, lm, "bmi ~ age")
    """
    if formula is not None:
        if expr is lm:
            return with_mids(data, formula=formula)
        if expr is glm:
            return with_mids(data, formula=formula, family=family or "binomial")
        if callable(expr):
            raise ValueError("with_(imp, callable, formula=...) requires lm or glm as callable")
        raise TypeError("formula= requires a callable analysis function as second argument")

    if isinstance(expr, str):
        return with_mids(data, formula=expr, family=family)

    if callable(expr):
        return with_mids(data, expr=expr)

    raise TypeError("expr must be a formula string or callable")


def summary(
    object: PoolResult,
    *,
    alpha: float = 0.05,
    **kwargs: Any,
) -> list[dict[str, float | str]]:
    """Summarize pooled estimates (R ``summary(mipo)``)."""
    if kwargs:
        raise TypeError(f"summary() got unexpected keyword arguments: {list(kwargs)}")
    if not isinstance(object, PoolResult):
        raise TypeError(f"summary() expects PoolResult, got {type(object).__name__}")
    return summary_pool(object, alpha=alpha)


def mice_mids(
    mids: Any,
    *,
    maxit: int = 5,
    max_iter: int | None = None,
    print: bool = False,
    print_flag: bool | None = None,
    verbose: bool | None = None,
    **kwargs: Any,
) -> Any:
    """Continue MICE on an existing mids object (R ``mice.mids``)."""
    from pymice.r_compat import resolve_maxit

    extra = normalize_mice_kwargs(kwargs)
    iterations = resolve_maxit(maxit=maxit, max_iter=max_iter)
    if "maxit" in extra:
        iterations = extra.pop("maxit")
    if "max_iter" in extra:
        iterations = resolve_maxit(maxit=iterations, max_iter=extra.pop("max_iter"))
    silent = resolve_print_flag(
        print=extra.pop("print", print),
        print_flag=print_flag,
        verbose=verbose,
        printFlag=extra.pop("printFlag", None),
    )
    return continue_imputation(
        mids,
        maxit=iterations,
        print=silent,
        **extra,
    )


def futuremice(
    data: Any,
    *,
    m: int = 5,
    maxit: int = 5,
    n_jobs: int | None = None,
    n_core: int | None = None,
    parallelseed: int | None = None,
    seed: int | None = None,
    print: bool = False,
    print_flag: bool | None = None,
    verbose: bool | None = None,
    **kwargs: Any,
) -> Any:
    """Parallel MICE chains (R ``futuremice``)."""
    extra = normalize_mice_kwargs(kwargs)
    workers = n_jobs or n_core or extra.pop("n_jobs", None) or extra.pop("n_core", None)
    print_flag = resolve_print_flag(
        print=extra.pop("print", print),
        print_flag=print_flag,
        verbose=verbose,
        printFlag=extra.pop("printFlag", None),
    )
    if "maxit" in extra:
        maxit = extra.pop("maxit")
    auto_core = workers is None
    return parallel_mice(
        data,
        m=m,
        n_jobs=workers,
        parallelseed=parallelseed,
        seed=seed,
        maxit=maxit,
        print=print_flag,
        announce_cores=auto_core and print_flag,
        **extra,
    )
