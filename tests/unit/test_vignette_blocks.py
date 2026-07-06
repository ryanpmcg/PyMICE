"""Tests for vignette block extraction and runner parsing."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

from lib.figure_map import REFERENCE_FIGURES, reference_images_for_step  # noqa: E402
from lib.vignette_blocks import (  # noqa: E402
    _is_plot_code,
    _md_pattern_plots,
    audit_vignette,
    build_manifest,
    parse_extracted_r,
    parse_runner_parts,
)

SAMPLE_R = """require(mice)
set.seed(123)

# --- code block ---

nhanes

# --- code block ---

##    age  bmi hyp chl
## 1    1   NA  NA  NA

# --- code block ---

summary(nhanes)

# --- code block ---

##       age            bmi
##  Min.   :1.00   Min.   :20.40

# --- code block ---

densityplot(nhanes$bmi)
"""


def test_md_pattern_default_is_plot():
    assert _md_pattern_plots("md.pattern(nhanes)")
    assert _is_plot_code("md.pattern(nhanes)")


def test_md_pattern_plot_false_is_console():
    assert not _md_pattern_plots("md.pattern(nhanes, plot = FALSE)")
    assert not _is_plot_code("md.pattern(nhanes, plot = FALSE)")


def test_v01_reference_figure_map():
    assert REFERENCE_FIGURES["01"][4] == ["fig_001.png"]
    assert REFERENCE_FIGURES["01"][7] == ["fig_002.png"]
    refs4 = reference_images_for_step("01", 4)
    refs7 = reference_images_for_step("01", 7)
    assert any(p.name == "fig_001.png" for p in refs4)
    assert any(p.name == "fig_002.png" for p in refs7)


def test_v03_reference_figure_map():
    assert REFERENCE_FIGURES["03"][6] == ["fig_003.png", "fig_005.png"]
    assert REFERENCE_FIGURES["03"][10] == ["fig_009.png"]
    assert REFERENCE_FIGURES["03"][15] == ["fig_010.png"]
    refs6 = reference_images_for_step("03", 6)
    assert [p.name for p in refs6] == ["fig_003.png", "fig_005.png"]


def test_v05_reference_figure_map():
    assert REFERENCE_FIGURES["05"][3] == ["fig_001.png", "fig_002.png"]
    assert REFERENCE_FIGURES["05"][4] == ["fig_003.png"]
    assert REFERENCE_FIGURES["05"][5] == ["fig_004.png", "fig_005.png", "fig_006.png"]
    assert REFERENCE_FIGURES["05"][6] == ["fig_007.png"]
    assert REFERENCE_FIGURES["05"][13] == ["fig_008.png"]
    assert REFERENCE_FIGURES["05"][14] == ["fig_009.png", "fig_010.png"]
    assert REFERENCE_FIGURES["05"][15] == ["fig_011.png", "fig_012.png", "fig_013.png"]
    assert REFERENCE_FIGURES["05"][18] == ["fig_014.png"]
    assert REFERENCE_FIGURES["05"][22] == [
        "fig_015.png",
        "fig_016.png",
        "fig_017.png",
        "fig_018.png",
        "fig_019.png",
    ]
    assert REFERENCE_FIGURES["05"][23] == [
        "fig_020.png",
        "fig_021.png",
        "fig_022.png",
        "fig_023.png",
        "fig_024.png",
    ]
    assert REFERENCE_FIGURES["05"][25] == ["fig_025.png", "fig_026.png", "fig_027.png"]
    assert REFERENCE_FIGURES["05"][26] == ["fig_028.png", "fig_029.png", "fig_030.png"]
    refs3 = reference_images_for_step("05", 3)
    assert [p.name for p in refs3] == ["fig_001.png", "fig_002.png"]
    refs22 = reference_images_for_step("05", 22)
    assert len(refs22) == 5


def test_v04_reference_figure_map():
    assert REFERENCE_FIGURES["04"][3] == ["fig_001.png"]
    assert REFERENCE_FIGURES["04"][5] == ["fig_003.png", "fig_004.png"]
    assert REFERENCE_FIGURES["04"][6] == ["fig_005.png"]
    assert REFERENCE_FIGURES["04"][8] == ["fig_008.png", "fig_007.png"]
    assert REFERENCE_FIGURES["04"][9] == ["fig_008.png", "fig_009.png", "fig_010.png"]
    refs5 = reference_images_for_step("04", 5)
    assert [p.name for p in refs5] == ["fig_003.png", "fig_004.png"]
    refs9 = reference_images_for_step("04", 9)
    assert [p.name for p in refs9] == ["fig_008.png", "fig_009.png", "fig_010.png"]


def test_parse_extracted_r_splits_code_and_output():
    blocks = parse_extracted_r(SAMPLE_R)
    assert len(blocks) == 4
    assert blocks[0].type == "setup"
    assert "nhanes" in blocks[1].r_code
    assert blocks[1].r_output.startswith("age  bmi hyp chl")
    assert "summary" in blocks[2].r_code
    assert blocks[2].r_output.startswith("age")
    assert blocks[3].type == "plot"


def test_parse_runner_parts_v01():
    parts = parse_runner_parts(ROOT / "devtools/runners/v01_ad_hoc_mice.py")
    assert parts
    assert any(p.step == 7 and "complete(imp)" in p.r_code for p in parts)


def test_build_manifest_v01():
    manifest = build_manifest("01")
    assert manifest.vignette == "01"
    assert len(manifest.blocks) > 20
    assert len(manifest.steps) == 14
    md_blocks = [b for b in manifest.blocks if "md.pattern(nhanes)" in b.r_code]
    assert md_blocks and md_blocks[0].type == "plot"
    assert md_blocks[0].figure == "fig_001.png"
    density_blocks = [b for b in manifest.blocks if "densityplot" in b.r_code]
    assert density_blocks and density_blocks[0].figure == "fig_002.png"
    out_path = ROOT / "reference/01_ad_hoc_and_mice/vignette_blocks.json"
    if not out_path.is_file():
        pytest.skip("run extract_vignette_blocks.py first")


def test_audit_v01_runs():
    blocks_path = ROOT / "reference/01_ad_hoc_and_mice/vignette_blocks.json"
    if not blocks_path.is_file():
        from lib.vignette_blocks import write_manifest

        write_manifest(build_manifest("01"))
    issues = audit_vignette("01")
    assert isinstance(issues, list)
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    assert not errors, [f"{i.category} step {i.step}: {i.message}" for i in errors]
    assert not warnings, [f"{i.category} step {i.step}: {i.message}" for i in warnings]


def test_audit_v02_runs():
    issues = audit_vignette("02")
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    assert not errors, [f"{i.category} step {i.step}: {i.message}" for i in errors]
    assert not warnings, [f"{i.category} step {i.step}: {i.message}" for i in warnings]


def test_audit_v05_runs():
    issues = audit_vignette("05")
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    assert not errors, [f"{i.category} step {i.step}: {i.message}" for i in errors]
    assert not warnings, [f"{i.category} step {i.step}: {i.message}" for i in warnings]


def test_audit_v06_runs():
    issues = audit_vignette("06")
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    assert not errors, [f"{i.category} step {i.step}: {i.message}" for i in errors]
    assert not warnings, [f"{i.category} step {i.step}: {i.message}" for i in warnings]


def test_audit_v03_runs():
    issues = audit_vignette("03")
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    assert not errors, [f"{i.category} step {i.step}: {i.message}" for i in errors]
    assert not warnings, [f"{i.category} step {i.step}: {i.message}" for i in warnings]


def test_audit_v04_runs():
    issues = audit_vignette("04")
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    assert not errors, [f"{i.category} step {i.step}: {i.message}" for i in errors]
    assert not warnings, [f"{i.category} step {i.step}: {i.message}" for i in warnings]


def test_audit_v07_runs():
    issues = audit_vignette("07")
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    assert not errors, [f"{i.category} step {i.step}: {i.message}" for i in errors]
    assert not warnings, [f"{i.category} step {i.step}: {i.message}" for i in warnings]


def test_audit_v08_runs():
    issues = audit_vignette("08")
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    assert not errors, [f"{i.category} step {i.step}: {i.message}" for i in errors]
    assert not warnings, [f"{i.category} step {i.step}: {i.message}" for i in warnings]
