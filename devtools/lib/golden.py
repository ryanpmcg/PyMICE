"""Load R vignette golden console output from ``golden_outputs.json``."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from lib.paths import REFERENCE_DIR
from lib.vignette_catalog import get_meta


def _strip_r_console_markers(text: str) -> str:
    """Remove R snapshot ``##`` prefixes so text matches runner formatters."""
    if not text:
        return ""
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            lines.append(line[3:])
        elif line == "##":
            lines.append("")
        elif line.startswith("##"):
            lines.append(line[2:].lstrip())
        else:
            lines.append(line)
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def _entry_records(data: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {k: v for k, v in data.items() if not k.startswith("_")}


@lru_cache(maxsize=16)
def _load_golden_file(vignette_dir: str) -> dict[str, dict[str, str]]:
    path = REFERENCE_DIR / vignette_dir / "golden_outputs.json"
    if not path.is_file():
        raise FileNotFoundError(f"golden_outputs.json not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return _entry_records(data)


def load_golden_outputs(vignette_num: str) -> dict[str, dict[str, str]]:
    """Return the raw golden store for a vignette (keys ``step.block_index``)."""
    meta = get_meta(vignette_num)
    return _load_golden_file(meta.vignette_dir)


def golden_entry(vignette_num: str, step: int, block: int) -> dict[str, str]:
    """Return one golden record (``r_code``, ``r_output``, metadata)."""
    meta = get_meta(vignette_num)
    data = _load_golden_file(meta.vignette_dir)
    key = f"{step}.{block}"
    entry = data.get(key)
    if entry is None:
        raise KeyError(
            f"golden_outputs.json missing key {key!r} for vignette {vignette_num} "
            f"({meta.vignette_dir})"
        )
    return entry


def golden_output(vignette_num: str, step: int, block: int, *, raw: bool = False) -> str:
    """
    Return expected R console text for a manifest block.

    Parameters
    ----------
    vignette_num
        Vignette number (``"01"`` … ``"08"``).
    step
        Numbered vignette step.
    block
        Global manifest block index (not sub-step index).
    raw
        When True, keep ``##`` prefixes from the extracted R snapshot.
    """
    text = golden_entry(vignette_num, step, block)["r_output"]
    return text if raw else _strip_r_console_markers(text)
