"""Parity manifest is the single source for vignette overview blurbs."""

from __future__ import annotations

import json

from lib.parity_manifest import MANIFEST_PATH, build_manifest


def test_parity_manifest_matches_builder() -> None:
    assert MANIFEST_PATH.exists(), "Run: python -m lib.parity_manifest (from devtools/)"
    on_disk = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert on_disk == build_manifest()
