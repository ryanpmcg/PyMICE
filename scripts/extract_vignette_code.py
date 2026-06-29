#!/usr/bin/env python3
"""Extract R code blocks from vignette HTML snapshots into vignette_extracted.R."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIGNETTES = ROOT / "Vignettes"


def extract_r_from_html(html: str) -> str:
    """Pull R source from pre/code blocks in knitr-style HTML."""
    chunks: list[str] = []
    for match in re.finditer(
        r'<pre[^>]*class="[^"]*r[^"]*"[^>]*>(.*?)</pre>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    ):
        text = match.group(1)
        text = re.sub(r"<[^>]+>", "", text)
        text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
        text = text.strip()
        if text:
            chunks.append(text)
    if not chunks:
        for match in re.finditer(r"<code[^>]*>(.*?)</code>", html, flags=re.DOTALL):
            text = re.sub(r"<[^>]+>", "", match.group(1)).strip()
            if text and len(text) > 20:
                chunks.append(text)
    header = "require(mice)\nrequire(lattice)\nset.seed(123)\n"
    body = "\n\n# --- code block ---\n\n".join(chunks)
    return header + "\n\n" + body + "\n"


def main() -> int:
    updated = 0
    for folder in sorted(VIGNETTES.glob("*_*")):
        html_path = folder / "vignette.html"
        if not html_path.exists():
            continue
        out_path = folder / "vignette_extracted.R"
        extracted = extract_r_from_html(html_path.read_text(encoding="utf-8", errors="replace"))
        out_path.write_text(extracted, encoding="utf-8")
        print(f"Wrote {out_path.relative_to(ROOT)} ({len(extracted)} bytes)")
        updated += 1
    if updated == 0:
        print("No vignette HTML files found.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
