"""Tests for golden_outputs.json loader."""

from __future__ import annotations

# devtools on path via tests/conftest.py
from lib.golden import golden_output, load_golden_outputs


def test_load_golden_outputs_v01():
    data = load_golden_outputs("01")
    assert "4.5" in data
    assert "md.pattern(nhanes)" in data["4.5"]["r_code"]


def test_golden_output_strips_markers():
    text = golden_output("01", 4, 5)
    assert not text.startswith("##")
    assert "13   1   1   1   1  0" in text


def test_golden_output_v02_predictor():
    text = golden_output("02", 2, 2)
    assert "age   0   1   1   1" in text
