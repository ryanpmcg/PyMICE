#!/usr/bin/env python3
"""Build canonical block manifests from R vignette snapshots."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEVTOOLS = ROOT / "devtools"
if str(DEVTOOLS) not in sys.path:
    sys.path.insert(0, str(DEVTOOLS))

from lib.vignette_blocks import (  # noqa: E402
    METAS,
    build_manifest,
    write_golden_outputs,
    write_manifest,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "vignettes",
        nargs="*",
        help="Vignette numbers (01–08). Default: all.",
    )
    parser.add_argument(
        "--golden",
        action="store_true",
        help="Also write golden_outputs.json per vignette.",
    )
    args = parser.parse_args()

    numbers = args.vignettes or sorted(METAS.keys())
    for num in numbers:
        key = num.zfill(2) if num.isdigit() else num
        if key not in METAS:
            print(f"Unknown vignette: {num}", file=sys.stderr)
            return 1
        manifest = build_manifest(key)
        path = write_manifest(manifest)
        rel = path.relative_to(ROOT)
        n_blocks = len(manifest.blocks)
        n_steps = len(manifest.steps)
        print(f"Wrote {rel} ({n_blocks} blocks, {n_steps} steps)")
        if args.golden:
            gpath = write_golden_outputs(manifest)
            print(f"  golden: {gpath.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
