"""RNG chain parity audit (requires R backend; run in nightly CI)."""

from __future__ import annotations

import pytest

pytest.importorskip("subprocess")

from audit_rng_parity import (
    audit_v01,
    audit_v02,
    audit_v03,
    audit_v03_pool,
    audit_v04,
    audit_v05,
)


@pytest.mark.parity
@pytest.mark.r_backend
@pytest.mark.slow
def test_rng_chain_parity_v01_v05() -> None:
    rows = audit_v01() + audit_v02() + audit_v03() + audit_v03_pool() + audit_v04() + audit_v05()
    failures = [r for r in rows if not r.matches]
    assert not failures, "\n".join(f"{r.vignette} {r.step}: {r.recommendation}" for r in failures)
