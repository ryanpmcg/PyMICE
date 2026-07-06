"""Draw-order parity tests for V02–V04 (scaffold; run after chain wiring + golden refresh)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DEVTOOLS = ROOT / "devtools"
BACKLOG = DEVTOOLS / "parity_backlog.json"


def _backlog_pending(vignette: str) -> list[dict]:
    if not BACKLOG.is_file():
        pytest.skip("Run devtools/audit_rng_parity.py to generate parity_backlog.json")
    items = json.loads(BACKLOG.read_text())
    return [
        item
        for item in items
        if item["vignette"] == vignette
        and item.get("chain_ready")
        and item.get("matches_now") is not True
    ]


@pytest.mark.skipif(
    subprocess.run(["which", "Rscript"], capture_output=True).returncode != 0,
    reason="Rscript not available",
)
@pytest.mark.parametrize("vignette", ["V02", "V03", "V04"])
def test_draw_order_backlog_pending(vignette: str) -> None:
    """Fails when backlog still has open chain/golden tasks (remove after step 3)."""
    pending = _backlog_pending(vignette)
    if pending:
        steps = ", ".join(p["step"] for p in pending)
        pytest.fail(f"{vignette} backlog still open: {steps}")
