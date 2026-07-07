#!/usr/bin/env python3
"""Execute all PyMICE vignette demos and write HTML/Markdown reports."""

from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

DEVTOOLS_DIR = Path(__file__).resolve().parent
ROOT = DEVTOOLS_DIR.parent

# Allow `from lib...` / `from runners...` when launched from repo root or devtools/
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(DEVTOOLS_DIR))

from lib.paths import VIGNETTES_PUBLISH_DIR  # noqa: E402

OUTPUT = VIGNETTES_PUBLISH_DIR
PAGES_VIGNETTES_URL = "https://ryanpmcg.github.io/PyMICE/vignettes/"

from lib.report import VignetteReport, write_reports  # noqa: E402
from lib.vignette_rng import ensure_vignette_r_prerequisites  # noqa: E402
from runners.v01_ad_hoc_mice import run as run_v01  # noqa: E402
from runners.v02_convergence_pooling import run as run_v02  # noqa: E402
from runners.v03_missingness import run as run_v03  # noqa: E402
from runners.v04_passive import run as run_v04  # noqa: E402
from runners.v05_multilevel import run as run_v05  # noqa: E402
from runners.v06_sensitivity import run as run_v06  # noqa: E402
from runners.v07_ampute import run as run_v07  # noqa: E402
from runners.v08_futuremice import run as run_v08  # noqa: E402

RUNNERS = [
    ("01", run_v01),
    ("02", run_v02),
    ("03", run_v03),
    ("04", run_v04),
    ("05", run_v05),
    ("06", run_v06),
    ("07", run_v07),
    ("08", run_v08),
]


def run_pytest_ci_subset() -> tuple[int, str]:
    """Run the same pytest subset as GitHub Actions (no R-backend tests)."""
    import io

    import pytest

    buffer = io.StringIO()
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = buffer
    sys.stderr = buffer
    try:
        exit_code = pytest.main(
            [
                "tests/",
                "-q",
                "--tb=line",
                "--ignore=tests/parity/test_rng_parity.py",
                "-m",
                "not r_backend",
            ]
        )
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    text = buffer.getvalue().strip() or "(pytest produced no output)"
    return int(exit_code), text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        metavar="NUM",
        help="Run a single vignette (01–08). Comma-separated for multiple.",
    )
    args = parser.parse_args()

    selected = RUNNERS
    if args.only:
        nums = {n.strip().zfill(2) for n in args.only.split(",") if n.strip()}
        selected = [(n, fn) for n, fn in RUNNERS if n in nums]
        unknown = nums - {n for n, _ in selected}
        if unknown:
            print(f"Unknown vignette(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            return 1

    print("Checking R prerequisites for vignette RNG (rng='r')...", flush=True)
    ensure_vignette_r_prerequisites()
    reports: list[VignetteReport] = []
    for num, run_fn in selected:
        try:
            print(f"Running Vignette {num}...", flush=True)
            report = run_fn()
        except Exception as exc:
            tb = traceback.format_exc()
            mod = run_fn.__module__.split(".")[-1]
            report = VignetteReport(
                number=num,
                slug=mod,
                title=mod,
                source_url="",
                status="Failed",
                error=f"{exc}\n\n{tb}",
            )
        reports.append(report)
        status = "ERROR" if report.error else "ok"
        print(f"Vignette {report.number}: {report.title} — {status}", flush=True)

    print("Running pytest (CI-equivalent subset)...", flush=True)
    exit_code, pytest_text = run_pytest_ci_subset()
    write_reports(OUTPUT, reports, pytest_text, pytest_exit_code=exit_code)

    index_html = OUTPUT / "index.html"
    print(f"\nReports written to: {OUTPUT}")
    print(f"Local:  {index_html}")
    print(f"Pages:  {PAGES_VIGNETTES_URL}")
    print("Commit docs/vignettes/ and push — GitHub Actions deploys with MkDocs.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
