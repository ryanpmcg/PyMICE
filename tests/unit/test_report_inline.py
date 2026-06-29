"""Markdown inline rendering for vignette HTML reports."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Commands"))

from lib.report import _inline_md


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
