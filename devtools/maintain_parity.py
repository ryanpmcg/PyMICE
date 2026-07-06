#!/usr/bin/env python3
"""Run structural + RNG parity audits and refresh parity_backlog.json."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DEVTOOLS = Path(__file__).resolve().parent
ROOT = DEVTOOLS.parent


def _run(script: str, *, label: str) -> int:
    path = DEVTOOLS / script
    print(f"\n{'=' * 80}")
    print(label)
    print(f"{'=' * 80}")
    proc = subprocess.run([sys.executable, str(path)], cwd=ROOT, check=False)
    return int(proc.returncode)


def main() -> int:
    steps = [
        ("audit_vignette_alignment.py", "Structural vignette alignment (V01–V08)"),
        ("audit_rng_parity.py", "RNG / draw-order re-compare (V01–V05 chains)"),
    ]
    codes = [_run(script, label=label) for script, label in steps]

    print(f"\n{'=' * 80}")
    print("Summary")
    print(f"{'=' * 80}")
    for (_, label), code in zip(steps, codes, strict=True):
        status = "OK" if code == 0 else f"exit {code}"
        print(f"  {label}: {status}")

    backlog = DEVTOOLS / "parity_backlog.json"
    if backlog.is_file():
        print(f"\nBacklog: {backlog}")

    if any(code != 0 for code in codes):
        return 1
    print("\nParity maintenance complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
