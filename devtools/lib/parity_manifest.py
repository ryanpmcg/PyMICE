"""Single source for vignette parity blurbs (index, pages, maintainer docs)."""

from __future__ import annotations

import json
from pathlib import Path

from lib.parity_docs import (
    V01_PARITY_OVERVIEW,
    V02_PARITY_OVERVIEW,
    V03_PARITY_OVERVIEW,
    V04_PARITY_OVERVIEW,
    V05_PARITY_OVERVIEW,
    V06_PARITY_OVERVIEW,
    V07_PARITY_OVERVIEW,
    V08_PARITY_OVERVIEW,
)
from lib.paths import REFERENCE_DIR
from lib.vignette_catalog import METAS

_OVERVIEWS = {
    "01": V01_PARITY_OVERVIEW,
    "02": V02_PARITY_OVERVIEW,
    "03": V03_PARITY_OVERVIEW,
    "04": V04_PARITY_OVERVIEW,
    "05": V05_PARITY_OVERVIEW,
    "06": V06_PARITY_OVERVIEW,
    "07": V07_PARITY_OVERVIEW,
    "08": V08_PARITY_OVERVIEW,
}

MANIFEST_PATH = REFERENCE_DIR / "parity_manifest.json"


def build_manifest() -> dict:
    vignettes = []
    for num in sorted(METAS.keys()):
        meta = METAS[num]
        vignettes.append(
            {
                "number": num,
                "slug": meta.slug,
                "title": meta.short_title,
                "source_url": meta.source_url,
                "reference_dir": meta.vignette_dir,
                "overview_md": _OVERVIEWS[num].strip(),
            }
        )
    return {"version": 1, "vignettes": vignettes}


def write_manifest(path: Path | None = None) -> Path:
    target = path or MANIFEST_PATH
    payload = build_manifest()
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    path = write_manifest()
    print(f"Wrote {path}")
