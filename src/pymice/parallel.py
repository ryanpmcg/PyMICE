"""Parallel MICE chains (``futuremice`` analogue)."""

from __future__ import annotations

import builtins
import os
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor
from typing import Any

import numpy as np

from pymice.engine import mice
from pymice.types import Mids, ibind

_PARALLELSEED_MIN = -999_999_999
_PARALLELSEED_MAX = 999_999_999


def distribute_imputations(m: int, n_core: int) -> list[int]:
    """
    Split ``m`` imputations across workers (R ``cut(1:m, n.core)`` tabulation).

    Returns a list of positive chunk sizes, one per active worker.
    """
    if m < 1:
        raise ValueError("m must be >= 1")
    if n_core < 1:
        raise ValueError("n_core must be >= 1")
    if n_core == 1:
        return [m]

    n_core = min(n_core, m)
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError(
            "distribute_imputations requires pandas. Install with: pip install pandas"
        ) from exc

    labels = [f"core{i}" for i in range(1, n_core + 1)]
    buckets = pd.cut(np.arange(1, m + 1), bins=n_core, labels=labels)
    counts = buckets.value_counts().reindex(labels, fill_value=0).astype(int)
    return [int(c) for c in counts.to_numpy() if c > 0]


def default_n_core(m: int) -> int:
    """Default worker count (R ``futuremice`` heuristic: min(m, logical cores))."""
    cores = os.cpu_count() or 1
    return max(1, min(m, cores))


def core_selection_message(n_core: int) -> str:
    """R-style console message when ``n.core`` is auto-selected."""
    return (
        "Number of cores not specified. Based on your machine a value of "
        f"n.core = {n_core} is chosen; the imputations are distributed about "
        "equally over the cores."
    )


def draw_parallelseed(rng: np.random.Generator | None = None) -> int:
    """Draw a reproducibility seed (R ``futuremice`` U(-1e9, 1e9) analogue)."""
    gen = rng if rng is not None else np.random.default_rng()
    return int(gen.integers(_PARALLELSEED_MIN, _PARALLELSEED_MAX, endpoint=False))


def resolve_parallel_seed(
    *,
    parallelseed: int | None,
    seed: int | None,
    n_core: int,
) -> tuple[int, int | None, bool]:
    """
    Resolve parallel and per-chain seeds.

    Returns ``(parallelseed, mice_seed, duplicate_imputations)``.
    """
    mice_seed = seed
    duplicate = mice_seed is not None and n_core > 1

    if parallelseed is not None:
        run_parallelseed = int(parallelseed)
    elif mice_seed is not None:
        from pymice.rng import RSession

        if RSession.is_active():
            run_parallelseed = int(RSession.session_seed())
        else:
            run_parallelseed = int(mice_seed)
    else:
        from pymice.rng import RSession

        if RSession.is_active():
            run_parallelseed = int(RSession.session_seed())
        else:
            run_parallelseed = draw_parallelseed()

    if duplicate:
        warnings.warn(
            "Be careful; specifying seed rather than parallelseed results in "
            "duplicate imputations across workers. Use parallelseed for unique, "
            "reproducible results.",
            UserWarning,
            stacklevel=3,
        )

    return run_parallelseed, mice_seed, duplicate


def worker_seeds(parallelseed: int, n_workers: int, *, duplicate: bool) -> list[int]:
    """Independent chain seeds derived from ``parallelseed`` (furrr-style streams)."""
    if duplicate:
        return [int(parallelseed)] * n_workers
    if n_workers == 1:
        return [int(parallelseed)]
    seq = np.random.SeedSequence(int(parallelseed))
    return [
        int(np.random.default_rng(child).integers(0, 2**31 - 1)) for child in seq.spawn(n_workers)
    ]


def _run_chunk(task: tuple[int, dict[str, Any]]) -> Mids:
    chunk_m, kwargs = task
    kw = dict(kwargs)
    kw["m"] = int(chunk_m)
    kw["n_jobs"] = 1
    return mice(**kw)


def _process_executor(workers: int) -> ProcessPoolExecutor:
    import multiprocessing as mp

    if workers <= 1:
        raise ValueError("workers must be > 1 for a process pool")
    if sys.platform == "linux":
        try:
            return ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("fork"))
        except ValueError:
            pass
    return ProcessPoolExecutor(max_workers=workers)


def merge_mids(results: list[Mids]) -> Mids:
    """Combine ``Mids`` objects by horizontally stacking imputations (R ``ibind``)."""
    if not results:
        raise ValueError("no mids objects to merge")
    merged = results[0]
    for item in results[1:]:
        merged = ibind(merged, item)
    return merged


def parallel_mice(
    data: Any,
    *,
    m: int = 5,
    n_jobs: int | None = None,
    n_core: int | None = None,
    parallelseed: int | None = None,
    print: bool = False,
    print_flag: bool | None = None,
    verbose: bool | None = None,
    announce_cores: bool = False,
    **kwargs: Any,
) -> Mids:
    """
    Run imputation chains in parallel (R ``futuremice`` workflow).

    Imputations are distributed across workers with ``cut(1:m, n.core)`` and
    merged via ``ibind``. Each worker runs ``mice(..., m=chunk_size)`` with an
    independent seed derived from ``parallelseed``.
    """
    from pymice.r_compat import resolve_print_flag

    print_flag = resolve_print_flag(print=print, print_flag=print_flag, verbose=verbose)

    if m < 1:
        raise ValueError("m must be >= 1")

    workers = n_jobs if n_jobs is not None else n_core
    auto_core = workers is None
    if workers is None:
        workers = default_n_core(m)
    workers = max(1, min(int(workers), m, os.cpu_count() or 1))

    mice_seed = kwargs.pop("seed", None)
    run_parallelseed, resolved_mice_seed, duplicate = resolve_parallel_seed(
        parallelseed=parallelseed,
        seed=mice_seed,
        n_core=workers,
    )

    if auto_core and (announce_cores or print_flag):
        builtins.print(core_selection_message(workers))

    chunks = distribute_imputations(m, workers)
    chain_seeds = worker_seeds(run_parallelseed, len(chunks), duplicate=duplicate)

    base_kwargs = {"data": data, "print": print_flag, **kwargs}
    if resolved_mice_seed is not None:
        base_kwargs["seed"] = int(resolved_mice_seed)

    tasks: list[tuple[int, dict[str, Any]]] = []
    for chunk_m, chain_seed in zip(chunks, chain_seeds, strict=True):
        kw = dict(base_kwargs)
        if not duplicate:
            kw["seed"] = int(chain_seed)
        tasks.append((chunk_m, kw))

    if len(tasks) == 1:
        result = _run_chunk(tasks[0])
    elif workers == 1:
        result = merge_mids([_run_chunk(task) for task in tasks])
    else:
        with _process_executor(workers) as executor:
            parts = list(executor.map(_run_chunk, tasks, chunksize=1))
        result = merge_mids(parts)

    result.parallelseed = run_parallelseed
    result.parallel_n_core = workers
    return result
