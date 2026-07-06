"""Fast structural alignment audit (no R imputation required)."""

from __future__ import annotations

import pytest
from lib.vignette_blocks import METAS, audit_vignette


@pytest.mark.parity
@pytest.mark.parametrize("vignette_num", sorted(METAS.keys()))
def test_vignette_structural_alignment(vignette_num: str) -> None:
    issues = audit_vignette(vignette_num)
    errors = [i for i in issues if i.severity == "error"]
    assert not errors, "\n".join(f"{e.category}: {e.message}" for e in errors)
