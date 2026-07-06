#!/usr/bin/env python3
"""Unified entry point to refresh R golden snapshots with provenance metadata.

Examples
--------
    python devtools/refresh_goldens.py --vignette 05,07
    python devtools/refresh_goldens.py --all
    python devtools/refresh_goldens.py --target draw_order
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

DEVTOOLS = Path(__file__).resolve().parent
ROOT = DEVTOOLS.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(DEVTOOLS))

TARGETS: dict[str, str] = {
    "05": "regenerate_v05_goldens",
    "06": "regenerate_v06_goldens",
    "07": "regenerate_v07_goldens",
    "draw_order": "regenerate_draw_order_goldens",
}


def _run_target(name: str) -> int:
    module_name = TARGETS[name]
    print(f"\n=== refresh {name} ({module_name}) ===")
    mod = importlib.import_module(module_name)
    return int(mod.main())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--vignette",
        metavar="LIST",
        help="Comma-separated targets: 05,06,07,draw_order",
    )
    group.add_argument("--all", action="store_true", help="Refresh every registered target.")
    group.add_argument(
        "--target",
        choices=sorted(TARGETS),
        help="Refresh a single named target.",
    )
    args = parser.parse_args(argv)

    if args.all:
        names = list(TARGETS)
    elif args.target:
        names = [args.target]
    else:
        names = [s.strip() for s in args.vignette.split(",") if s.strip()]

    unknown = [n for n in names if n not in TARGETS]
    if unknown:
        parser.error(f"Unknown target(s): {', '.join(unknown)}. Choose from {', '.join(TARGETS)}")

    codes = [_run_target(n) for n in names]
    if any(c != 0 for c in codes):
        return 1
    print("\nGolden refresh complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
