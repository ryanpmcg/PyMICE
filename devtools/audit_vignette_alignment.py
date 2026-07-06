#!/usr/bin/env python3
"""Audit PyMICE vignette runners against canonical block manifests."""

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
    audit_vignette,
    format_audit_report,
)

OUTPUT = DEVTOOLS / "output"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "vignettes",
        nargs="*",
        help="Vignette numbers (01–08). Default: all.",
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with code 1 when any error-level issue is found.",
    )
    args = parser.parse_args()

    numbers = args.vignettes or sorted(METAS.keys())
    OUTPUT.mkdir(parents=True, exist_ok=True)
    exit_code = 0

    for num in numbers:
        key = num.zfill(2) if num.isdigit() else num
        if key not in METAS:
            print(f"Unknown vignette: {num}", file=sys.stderr)
            return 1
        issues = audit_vignette(key)
        report = format_audit_report(key, issues)
        out_path = OUTPUT / f"alignment_audit_V{key}.md"
        out_path.write_text(report, encoding="utf-8")
        rel = out_path.relative_to(ROOT)
        errors = sum(1 for i in issues if i.severity == "error")
        warnings = sum(1 for i in issues if i.severity == "warning")
        print(f"Wrote {rel} ({errors} errors, {warnings} warnings)")
        if errors and args.fail_on_error:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
