"""Structured parity backlog for vignettes V02–V04 (steps 3–4 of parity process)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class ParityCategory(str, Enum):
    STALE_GOLDEN = "stale_golden"
    DRAW_ORDER = "draw_order"
    ALGORITHM = "algorithm"
    COSMETIC = "cosmetic"
    INTENTIONAL = "intentional"


@dataclass(frozen=True)
class ParityTask:
    vignette: str
    step: str
    category: ParityCategory
    partial_reason: str
    recommendation: str
    priority: int
    matches_now: bool | None = None
    chain_ready: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        return d


BACKLOG_PATH = Path(__file__).resolve().parents[1] / "parity_backlog.json"


def default_backlog() -> list[ParityTask]:
    """Tracked draw-order items; refreshed by ``audit_rng_parity.py`` / ``maintain_parity.py``."""
    return [
        ParityTask(
            "V02",
            "7–8 imp3 mira/pool",
            ParityCategory.DRAW_ORDER,
            "imp3 chain aligned; goldens refreshed 2026-07-05",
            "Re-run maintain_parity.py after chain changes",
            priority=1,
            matches_now=True,
            chain_ready=True,
        ),
        ParityTask(
            "V02",
            "4 imp$meth",
            ParityCategory.STALE_GOLDEN,
            "imp_conv_seed meth step matches golden",
            "Re-run maintain_parity.py after chain changes",
            priority=2,
            matches_now=True,
            chain_ready=True,
        ),
        ParityTask(
            "V03",
            "8 summary(complete(imp1))",
            ParityCategory.STALE_GOLDEN,
            "run_v03_boys_chain; golden refreshed 2026-07-05",
            "Re-run maintain_parity.py after chain changes",
            priority=1,
            matches_now=True,
            chain_ready=True,
        ),
        ParityTask(
            "V03",
            "8 with(imp1, mean(tv))",
            ParityCategory.DRAW_ORDER,
            "TV means follow PMM imp1 draw order",
            "Re-run maintain_parity.py after chain changes",
            priority=1,
            matches_now=True,
            chain_ready=True,
        ),
        ParityTask(
            "V03",
            "11–14 mammalsleep pool",
            ParityCategory.DRAW_ORDER,
            "run_v03_mammalsleep_chain; pool goldens refreshed",
            "Re-run maintain_parity.py after chain changes",
            priority=2,
            matches_now=True,
            chain_ready=True,
        ),
        ParityTask(
            "V04",
            "2 pas.imp",
            ParityCategory.DRAW_ORDER,
            "run_v04_chain: pas.imp seed=123, boys unseeded",
            "Re-run maintain_parity.py after chain changes",
            priority=1,
            matches_now=True,
            chain_ready=True,
        ),
        ParityTask(
            "V04",
            "5 table(tv)",
            ParityCategory.DRAW_ORDER,
            "boys chain-aligned TV frequency tables",
            "Re-run maintain_parity.py after chain changes",
            priority=1,
            matches_now=True,
            chain_ready=True,
        ),
        ParityTask(
            "V01",
            "13 print(imp)",
            ParityCategory.COSMETIC,
            "format_mids_print_r excludes non-imputed age from visitSequence",
            "Resolved 2026-07-05",
            priority=3,
            matches_now=True,
            chain_ready=True,
        ),
        ParityTask(
            "V01",
            "8–9 norm.predict",
            ParityCategory.ALGORITHM,
            "OLS norm.predict implementation tolerance",
            "Keep partial with atol; optional R lm backend later",
            priority=4,
            matches_now=True,
            chain_ready=True,
        ),
        ParityTask(
            "V06",
            "11–13 Cox/pool/qbar",
            ParityCategory.DRAW_ORDER,
            "δ-chain + lifelines Cox; goldens refreshed 2026-07-05",
            "Re-run regenerate_v06_goldens.py after Cox chain changes",
            priority=1,
            matches_now=True,
            chain_ready=True,
        ),
        ParityTask(
            "V05",
            "21–26 multilevel diagnostics",
            ParityCategory.ALGORITHM,
            "2l.norm/2l.pan sampler moments differ from R",
            "Documented ~0.15 moment tolerance; setup matrices exact",
            priority=2,
            matches_now=True,
            chain_ready=True,
        ),
    ]


def save_backlog(tasks: list[ParityTask], path: Path | None = None) -> Path:
    target = path or BACKLOG_PATH
    payload = [t.to_dict() for t in tasks]
    target.write_text(json.dumps(payload, indent=2) + "\n")
    return target


def load_backlog(path: Path | None = None) -> list[ParityTask]:
    target = path or BACKLOG_PATH
    if not target.is_file():
        return default_backlog()
    raw = json.loads(target.read_text())
    return [
        ParityTask(
            vignette=item["vignette"],
            step=item["step"],
            category=ParityCategory(item["category"]),
            partial_reason=item["partial_reason"],
            recommendation=item["recommendation"],
            priority=item["priority"],
            matches_now=item.get("matches_now"),
            chain_ready=item.get("chain_ready", False),
        )
        for item in raw
    ]
