"""Physics-aware post-processing for WEPPCLIFF weather variables."""

from __future__ import annotations

from pymice.postprocess import post_squeeze


def temperature_posts(column_names: list[str]) -> dict[str, object]:
    """Return post hooks that keep temperatures in plausible absolute ranges (°C)."""
    posts: dict[str, object] = {}
    if "MIN_TEMP" in column_names:
        posts["MIN_TEMP"] = post_squeeze(-60.0, 55.0)
    if "MAX_TEMP" in column_names:
        posts["MAX_TEMP"] = post_squeeze(-55.0, 60.0)
    return posts


def non_negative_posts(column_names: list[str]) -> dict[str, object]:
    posts: dict[str, object] = {}
    for name in ("PRECIP", "DUR", "SO_RAD", "W_VEL"):
        if name in column_names:
            posts[name] = post_squeeze(0.0, 1e6)
    return posts
