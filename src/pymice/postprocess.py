"""Post-processing hooks during MICE iterations (R ``post`` / ``squeeze``)."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

PostHook = str | Callable[["PostContext"], None]


@dataclass
class PostContext:
    """Mutable context passed to post-processing hooks."""

    imp: dict[str, NDArray[np.float64]]
    data: NDArray[np.float64]
    column_names: list[str]
    name: str
    imp_num: int
    observed: NDArray[np.bool_]
    where: NDArray[np.bool_]
    extras: dict[str, Any] = field(default_factory=dict)

    @property
    def imp_col(self) -> NDArray[np.float64]:
        return self.imp[self.name][:, self.imp_num]

    def set_imp(self, values: NDArray[np.float64]) -> None:
        self.imp[self.name][:, self.imp_num] = np.asarray(values, dtype=np.float64)


def squeeze(
    values: NDArray[np.floating],
    bounds: tuple[float, float] | NDArray[np.floating],
) -> NDArray[np.float64]:
    """Clip imputed values to bounds (R ``mice::squeeze``)."""
    arr = np.asarray(values, dtype=np.float64)
    b = np.asarray(bounds, dtype=np.float64).ravel()
    if b.size != 2:
        raise ValueError("bounds must contain exactly two values (low, high)")
    return np.clip(arr, float(b[0]), float(b[1]))


def post_squeeze(lo: float, hi: float) -> Callable[[PostContext], None]:
    def _fn(ctx: PostContext) -> None:
        ctx.set_imp(squeeze(ctx.imp_col, (lo, hi)))

    return _fn


def post_add(delta: float) -> Callable[[PostContext], None]:
    def _fn(ctx: PostContext) -> None:
        ctx.set_imp(ctx.imp_col + delta)

    return _fn


def _substitute_extras(cmd: str, extras: dict[str, Any]) -> str:
    out = cmd
    for key, val in extras.items():
        out = re.sub(rf"\b{re.escape(key)}\b", str(val), out)
    return out


def execute_post(cmd: PostHook, ctx: PostContext) -> None:
    """Run a post command (Python callable or R-style string)."""
    if callable(cmd):
        cmd(ctx)
        return
    if not cmd or not str(cmd).strip():
        return

    s = _substitute_extras(str(cmd).strip(), ctx.extras)

    m = re.match(
        r"imp\[\[j\]\]\[, ?i\] <- squeeze\(imp\[\[j\]\]\[, ?i\], c\(([^)]+)\)\)",
        s,
        flags=re.IGNORECASE,
    )
    if m:
        parts = [float(x.strip()) for x in m.group(1).split(",")]
        ctx.set_imp(squeeze(ctx.imp_col, (parts[0], parts[1])))
        return

    m = re.match(
        r"imp\[\[j\]\]\[, ?i\] <- imp\[\[j\]\]\[, ?i\] \+ (.+)",
        s,
        flags=re.IGNORECASE,
    )
    if m:
        ctx.set_imp(ctx.imp_col + float(m.group(1).strip()))
        return

    raise ValueError(f"unsupported post command: {cmd!r}")


def normalize_post(
    column_names: list[str],
    post: dict[str, PostHook] | list[str] | None,
) -> dict[str, PostHook]:
    if post is None:
        return {name: "" for name in column_names}
    if isinstance(post, list):
        if len(post) != len(column_names):
            raise ValueError("post list length must match number of columns")
        return dict(zip(column_names, post, strict=True))
    out = {name: "" for name in column_names}
    for key, val in post.items():
        if key not in column_names:
            raise ValueError(f"unknown variable in post: {key!r}")
        out[key] = val
    return out
