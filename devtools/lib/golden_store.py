"""Read/write ``golden_outputs.json`` with provenance metadata."""

from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.paths import REFERENCE_DIR

PROVENANCE_KEY = "_provenance"


def golden_path(vignette_dir: str) -> Path:
    return REFERENCE_DIR / vignette_dir / "golden_outputs.json"


def _to_r_output(text: str) -> str:
    lines = [f"## {line}" if line.strip() else "##" for line in text.splitlines()]
    return "\n".join(lines)


def _r_version() -> str:
    try:
        out = subprocess.run(
            ["Rscript", "-e", "cat(as.character(getRversion()))"],
            check=True,
            capture_output=True,
            text=True,
        )
        return out.stdout.strip() or "unknown"
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unavailable"


def _mice_version() -> str:
    try:
        out = subprocess.run(
            ["Rscript", "-e", 'cat(as.character(packageVersion("mice")))'],
            check=True,
            capture_output=True,
            text=True,
        )
        return out.stdout.strip() or "unknown"
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unavailable"


def provenance_block(*, pymice_version: str = "0.1.0") -> dict[str, str]:
    return {
        "refreshed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "python_version": platform.python_version(),
        "pymice_version": pymice_version,
        "r_version": _r_version(),
        "mice_version": _mice_version(),
        "platform": platform.platform(),
    }


def load_golden_data(vignette_dir: str) -> dict[str, Any]:
    path = golden_path(vignette_dir)
    return json.loads(path.read_text(encoding="utf-8"))


def entry_keys(data: dict[str, Any]) -> list[str]:
    return [k for k in data if not k.startswith("_")]


def update_golden_key(
    vignette_dir: str,
    key: str,
    r_output: str,
    *,
    refresh_provenance: bool = True,
    pymice_version: str = "0.1.0",
) -> None:
    path = golden_path(vignette_dir)
    data = load_golden_data(vignette_dir)
    if key not in data or key.startswith("_"):
        raise KeyError(f"{path}: missing entry {key!r}")
    data[key]["r_output"] = _to_r_output(r_output)
    if refresh_provenance:
        data[PROVENANCE_KEY] = provenance_block(pymice_version=pymice_version)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"updated {vignette_dir} {key}")
