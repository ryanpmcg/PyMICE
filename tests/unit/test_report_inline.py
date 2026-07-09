"""Markdown inline rendering for vignette HTML reports."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "devtools"))

from lib.r_style import format_tutorial_step_md
from lib.report import _inline_md, blocks_to_html, parse_blocks


def test_inline_md_italic():
    assert "<em>age group</em>" in _inline_md("*age group*")


def test_inline_md_bold_and_italic():
    html = _inline_md("**bold** and *italic* and `code`")
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html
    assert "<code>code</code>" in html


def test_inline_md_link():
    html = _inline_md("[original](https://example.com)")
    assert '<a href="https://example.com">original</a>' in html


def test_long_output_renders_side_by_side_tabs():
    long_out = "\n".join(f"line {i}" for i in range(50))
    md = format_tutorial_step_md(
        "help(nhanes)",
        "print(format_help_r('nhanes'))",
        long_out,
        r_expected="R help text",
    )
    html = blocks_to_html(parse_blocks(md))
    assert "dual-code-tabs" in html
    assert "Side-by-Side" in html
    assert ">R code<" not in html
    assert "```text" not in html
    assert '<details class="long-output">' in html
