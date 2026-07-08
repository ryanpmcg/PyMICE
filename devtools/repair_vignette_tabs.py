#!/usr/bin/env python3
"""Repair orphaned R/Python blocks in published vignette HTML (legacy long-output markdown)."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

DEVTOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(DEVTOOLS))

import lib.report as report  # noqa: E402
from lib.report import render_dual_code_tabs  # noqa: E402

VIGNETTES_DIR = DEVTOOLS.parent / "docs" / "vignettes"

_PRE = re.compile(
    r'<pre class="language-(\w+)"><code[^>]*>(.*?)</code></pre>',
    re.DOTALL,
)

_ORPHAN = re.compile(
    r"<h5>R code</h5>\s*"
    r"(<pre class=\"language-r\"><code[^>]*>.*?</code></pre>)\s*"
    r"(?:(<h5>R output</h5>\s*(<pre class=\"language-text\"><code[^>]*>.*?</code></pre>))\s*)?"
    r"<h5>Python code</h5>\s*"
    r"(<pre class=\"language-python\"><code[^>]*>.*?</code></pre>)\s*"
    r"(<details class=\"long-output\"[^>]*>.*?</details>"
    r"|<h5>Output</h5>\s*<pre class=\"language-(\w+)\"><code[^>]*>.*?</code></pre>)",
    re.DOTALL,
)


def _code_from_pre(pre_html: str) -> str:
    match = _PRE.search(pre_html)
    if not match:
        return ""
    return html.unescape(match.group(2))


def _output_from_tail(tail: str, explicit_lang: str | None) -> tuple[str, str]:
    if tail.startswith("<details"):
        fence = re.search(r"```(\w+)\s*\n(.*?)\n```", tail, re.DOTALL)
        if fence:
            return fence.group(1), html.unescape(fence.group(2))
        return "text", ""
    match = _PRE.search(tail)
    if not match:
        return explicit_lang or "text", ""
    return match.group(1), html.unescape(match.group(2))


def _sync_tab_index(text: str) -> None:
    ids = [int(n) for n in re.findall(r'id="(?:code|tabs|plots)-(\d+)"', text)]
    report._tab_index = max(ids) if ids else 0


def repair_html(text: str) -> tuple[str, int]:
    _sync_tab_index(text)
    fixes = 0

    def _replace(match: re.Match[str]) -> str:
        nonlocal fixes
        r_code = _code_from_pre(match.group(1))
        r_out = _code_from_pre(match.group(3)) if match.group(3) else ""
        py_code = _code_from_pre(match.group(4))
        out_lang, out_code = _output_from_tail(match.group(5), match.group(6))
        fixes += 1
        return render_dual_code_tabs(
            r_code,
            py_code,
            out_code,
            out_lang,
            r_out=r_out,
        )

    return _ORPHAN.sub(_replace, text), fixes


def main() -> int:
    total = 0
    for path in sorted(VIGNETTES_DIR.glob("v*.html")):
        original = path.read_text(encoding="utf-8")
        repaired, n = repair_html(original)
        if n:
            path.write_text(repaired, encoding="utf-8", newline="\n")
            print(f"{path.name}: repaired {n} block(s)")
            total += n
        else:
            print(f"{path.name}: ok")
    print(f"Total repairs: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())