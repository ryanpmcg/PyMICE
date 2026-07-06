"""Map vignette step numbers to extracted R reference figure filenames."""

from __future__ import annotations

from pathlib import Path

from lib.paths import REFERENCE_DIR
from lib.vignette_catalog import get_meta

_VIGNETTES = REFERENCE_DIR

# step number -> list of fig_XXX filenames in reference/<dir>/reference_figures/
REFERENCE_FIGURES: dict[str, dict[int, list[str]]] = {
    "01": {4: ["fig_001.png"], 7: ["fig_002.png"]},
    "02": {
        3: ["fig_001.png"],
        4: ["fig_002.png"],
        5: ["fig_003.png"],
        6: ["fig_004.png", "fig_005.png"],
    },
    "03": {
        6: ["fig_003.png", "fig_005.png"],
        10: ["fig_009.png"],
        15: ["fig_010.png"],
    },
    "04": {
        3: ["fig_001.png"],
        5: ["fig_003.png", "fig_004.png"],
        6: ["fig_005.png"],
        8: ["fig_008.png", "fig_007.png"],
        9: ["fig_008.png", "fig_009.png", "fig_010.png"],
    },
    "05": {
        3: ["fig_001.png", "fig_002.png"],
        4: ["fig_003.png"],
        5: ["fig_004.png", "fig_005.png", "fig_006.png"],
        6: ["fig_007.png"],
        13: ["fig_008.png"],
        14: ["fig_009.png", "fig_010.png"],
        15: ["fig_011.png", "fig_012.png", "fig_013.png"],
        18: ["fig_014.png"],
        22: ["fig_015.png", "fig_016.png", "fig_017.png", "fig_018.png", "fig_019.png"],
        23: ["fig_020.png", "fig_021.png", "fig_022.png", "fig_023.png", "fig_024.png"],
        25: ["fig_025.png", "fig_026.png", "fig_027.png"],
        26: ["fig_028.png", "fig_029.png", "fig_030.png"],
    },
    "06": {
        4: ["fig_001.png"],
        5: ["fig_002.png"],
        8: ["fig_003.png", "fig_004.png"],
        9: ["fig_005.png", "fig_006.png"],
        10: ["fig_007.png", "fig_008.png"],
    },
    "07": {
        6: ["fig_009.png"],
        7: ["fig_010.png"],
        8: ["fig_011.png"],
    },
    "08": {},
}


def reference_images_for_step(number: str, step: int) -> list[Path]:
    """Resolved paths to R reference figures for a numbered step (may be empty)."""
    meta = get_meta(number)
    names = REFERENCE_FIGURES.get(meta.number, {}).get(step, [])
    base = _VIGNETTES / meta.vignette_dir / "reference_figures"
    return [base / name for name in names if (base / name).is_file()]


def copy_reference_assets(output_assets: Path) -> None:
    """Copy reference figures into report assets/reference/<slug>/ for HTML."""
    ref_root = output_assets / "reference"
    ref_root.mkdir(parents=True, exist_ok=True)
    for num in REFERENCE_FIGURES:
        meta = get_meta(num)
        src_dir = _VIGNETTES / meta.vignette_dir / "reference_figures"
        if not src_dir.is_dir():
            continue
        dest = ref_root / meta.slug
        dest.mkdir(parents=True, exist_ok=True)
        for path in src_dir.iterdir():
            if path.is_file():
                target = dest / path.name
                if not target.exists() or path.stat().st_mtime > target.stat().st_mtime:
                    target.write_bytes(path.read_bytes())
