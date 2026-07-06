"""R ``mice`` diagnostic theme colors (``mdc()`` / ``mice.theme`` palette)."""

from __future__ import annotations

import math
from typing import Literal

SymbolLine = Literal["symbol", "line", "sym", "lin"]
Role = Literal["observed", "missing", "both", "obs", "mis"]

# R ``mdc()`` defaults (``grDevices::hcl`` with alpha when supported).
_MDC_HCL: dict[str, tuple[float, float, float, float]] = {
    "cso": (240.0, 100.0, 40.0, 0.7),
    "csi": (0.0, 100.0, 40.0, 0.7),
    "csc": (0.0, 0.0, 50.0, 1.0),
    "clo": (240.0, 100.0, 40.0, 0.8),
    "cli": (0.0, 100.0, 40.0, 0.8),
    "clc": (0.0, 0.0, 50.0, 1.0),
}

_ROLE_INDEX = {"observed": 0, "obs": 0, "missing": 1, "mis": 1, "both": 2}
_STYLE_OFFSET = {"symbol": 0, "sym": 0, "line": 3, "lin": 3}
_ORDER = ("cso", "csi", "csc", "clo", "cli", "clc")


def _hcl_to_rgb01(
    h: float, c: float, l: float, alpha: float = 1.0
) -> tuple[float, float, float, float]:
    """Approximate R ``grDevices::hcl`` as linear sRGB (0–1) + alpha."""
    if c <= 0:
        gray = l / 100.0
        return gray, gray, gray, alpha

    h_rad = math.radians(h)
    a = c * math.cos(h_rad)
    b = c * math.sin(h_rad)
    y = (l + 16.0) / 116.0
    x = a / 500.0 + y
    z = y - b / 200.0
    d = 6.0 / 29.0

    def _f_inv(t: float) -> float:
        return t**3 if t > d else 3.0 * d**2 * (t - 4.0 / 29.0)

    x_xyz = 0.95047 * _f_inv(x)
    y_xyz = 1.00000 * _f_inv(y)
    z_xyz = 1.08883 * _f_inv(z)
    r_lin = 3.2406 * x_xyz - 1.5372 * y_xyz - 0.4986 * z_xyz
    g_lin = -0.9689 * x_xyz + 1.8758 * y_xyz + 0.0415 * z_xyz
    b_lin = 0.0557 * x_xyz - 0.2040 * y_xyz + 1.0570 * z_xyz

    def _gamma(u: float) -> float:
        return 12.92 * u if u <= 0.0031308 else 1.055 * u ** (1.0 / 2.4) - 0.055

    return (
        _gamma(max(0.0, min(1.0, r_lin))),
        _gamma(max(0.0, min(1.0, g_lin))),
        _gamma(max(0.0, min(1.0, b_lin))),
        alpha,
    )


def _rgba_tuple(name: str, *, transparent: bool = True) -> tuple[float, float, float, float]:
    h, c, l, a = _MDC_HCL[name]
    if not transparent and name in {"cso", "csi", "clo", "cli"}:
        a = 1.0
    if name in {"csc", "clc"}:
        gray = l / 100.0
        return gray, gray, gray, 1.0
    return _hcl_to_rgb01(h, c, l, a)


def mdc(
    role: int | str | list[int | str],
    style: SymbolLine | list[SymbolLine] = "symbol",
    *,
    transparent: bool = True,
    as_hex: bool = False,
) -> str | tuple[float, float, float, float] | list[str | tuple[float, float, float, float]]:
    """
    Return mice diagnostic colors (R ``mdc()``).

    Examples
    --------
    >>> mdc(1)  # observed symbol blue
    >>> mdc(["obs", "mis"], "line")
    >>> mdc(1, as_hex=True)
    """
    roles = [role] if isinstance(role, (int, str)) else list(role)
    styles = [style] if isinstance(style, str) else list(style)

    def _one(r: int | str, s: SymbolLine) -> str | tuple[float, float, float, float]:
        if isinstance(r, int):
            if r < 1 or r > 6:
                raise ValueError("mdc numeric codes must be 1..6")
            key = _ORDER[r - 1]
        else:
            idx = _ROLE_INDEX.get(str(r).lower())
            if idx is None:
                raise ValueError(f"unknown mdc role: {r!r}")
            offset = _STYLE_OFFSET.get(s if isinstance(s, str) else "symbol", 0)
            key = _ORDER[idx + offset]

        rgba = _rgba_tuple(key, transparent=transparent)
        if not as_hex:
            return rgba
        r8, g8, b8, a8 = (round(ch * 255) for ch in rgba)
        if a8 >= 255:
            return f"#{r8:02x}{g8:02x}{b8:02x}"
        return f"#{r8:02x}{g8:02x}{b8:02x}{a8:02x}"

    out: list[str | tuple[float, float, float, float]] = []
    for r in roles:
        for s in styles:
            out.append(_one(r, s))

    if isinstance(role, (int, str)) and isinstance(style, str):
        return out[0]
    return out


# Named constants for plot code (matplotlib-friendly RGBA tuples).
COLOR_OBSERVED = mdc(1)
COLOR_MISSING = mdc(2)
COLOR_COMBINED = mdc(3)
COLOR_OBSERVED_LINE = mdc(4)
COLOR_MISSING_LINE = mdc(5)
COLOR_COMBINED_LINE = mdc(6)
