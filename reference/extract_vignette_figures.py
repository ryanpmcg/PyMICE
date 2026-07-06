#!/usr/bin/env python3
"""Extract embedded PNG figures from R vignette HTML snapshots."""

from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
IMG_RE = re.compile(
    r'<img[^>]+src="data:image/(?P<fmt>[^;]+);base64,(?P<data>[^"]+)"',
    re.IGNORECASE,
)


def extract_figures(html_path: Path, out_dir: Path) -> list[str]:
    text = html_path.read_text(encoding="utf-8", errors="replace")
    out_dir.mkdir(parents=True, exist_ok=True)
    names: list[str] = []
    for idx, match in enumerate(IMG_RE.finditer(text), start=1):
        fmt = match.group("fmt").lower()
        ext = "jpg" if fmt in {"jpeg", "jpg"} else fmt
        if ext not in {"png", "gif", "webp", "jpg"}:
            ext = "png"
        name = f"fig_{idx:03d}.{ext}"
        out_dir.joinpath(name).write_bytes(base64.b64decode(match.group("data")))
        names.append(name)
    return names


def main() -> int:
    targets = (
        [Path(p) for p in sys.argv[1:]]
        if len(sys.argv) > 1
        else sorted(REFERENCE.glob("*/vignette.html"))
    )
    for html_path in targets:
        out_dir = html_path.parent / "reference_figures"
        names = extract_figures(html_path, out_dir)
        rel = out_dir.relative_to(ROOT) if out_dir.is_relative_to(ROOT) else out_dir
        print(f"Wrote {len(names)} figures to {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
