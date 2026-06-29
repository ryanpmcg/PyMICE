#!/usr/bin/env python3
"""Execute all PyMICE vignette demos and write HTML/Markdown reports."""

from __future__ import annotations

import subprocess
import sys
import traceback
from pathlib import Path

COMMANDS_DIR = Path(__file__).resolve().parent
ROOT = COMMANDS_DIR.parent
OUTPUT = COMMANDS_DIR / "output"

# Allow `from Commands...` and `from lib...` when launched from repo root or Commands/
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(COMMANDS_DIR))

from lib.report import VignetteReport, write_reports  # noqa: E402
from vignettes.v01_ad_hoc_mice import run as run_v01  # noqa: E402
from vignettes.v02_convergence_pooling import run as run_v02  # noqa: E402
from vignettes.v03_missingness import run as run_v03  # noqa: E402
from vignettes.v04_passive import run as run_v04  # noqa: E402
from vignettes.v05_multilevel import run as run_v05  # noqa: E402
from vignettes.v06_sensitivity import run as run_v06  # noqa: E402
from vignettes.v07_ampute import run as run_v07  # noqa: E402
from vignettes.v08_futuremice import run as run_v08  # noqa: E402

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


def run_pytest() -> tuple[int, str]:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-q",
    ]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    text = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return proc.returncode, text.strip()


def main() -> int:
    reports: list[VignetteReport] = []
    for num, run_fn in RUNNERS:
        try:
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
        print(f"Vignette {report.number}: {report.title} — {status}")

    exit_code, pytest_text = run_pytest()
    write_reports(OUTPUT, reports, pytest_text)

    index_html = OUTPUT / "index.html"
    print(f"\nReports written to: {OUTPUT}")
    print(f"Open: {index_html}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
