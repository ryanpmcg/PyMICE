"""Published vignette HTML must use side-by-side tabs for all R/Python steps."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIGNETTES = ROOT / "docs" / "vignettes"


def test_published_vignettes_have_no_orphan_code_blocks():
    errors: list[str] = []
    for path in sorted(VIGNETTES.glob("v*.html")):
        text = path.read_text(encoding="utf-8")
        if re.search(r">R [Cc]ode<", text):
            errors.append(f"{path.name}: standalone R code heading (missing side-by-side tabs)")
        if "```text" in text:
            errors.append(f"{path.name}: unparsed markdown fence in HTML")
        dual = len(re.findall(r'class="code-tabs dual-code-tabs"', text))
        plots = len(re.findall(r'class="code-tabs plot-tabs"', text))
        side = len(re.findall(r">Side-by-Side<", text))
        expected = dual + plots
        if side != expected:
            errors.append(
                f"{path.name}: {side} Side-by-Side buttons vs {expected} tab panels "
                f"({dual} code + {plots} plot)"
            )
    assert not errors, "\n".join(errors)
