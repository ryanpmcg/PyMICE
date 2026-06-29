"""Load and query Köppen–Geiger prior statistics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_DEFAULT_PATH = Path(__file__).with_name("default_priors.json")


@dataclass(frozen=True)
class VarPrior:
    mean: float
    std: float


def infer_koppen_zone(lat: float, lon: float = 0.0) -> str:
    """
    Heuristic Köppen zone from latitude (override with ``-kg`` in WEPPCLIFF).

    Full raster lookup is deferred; this covers common mid-latitude cases.
    """
    del lon
    alat = abs(float(lat))
    if alat < 23.5:
        return "Am"
    if alat < 35.0:
        return "BSk" if alat < 30.0 else "Cfa"
    if alat < 50.0:
        return "Cfa"
    return "Dfb"


class KoppenPriorStore:
    """Seasonal marginal priors by Köppen zone."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.version = int(data.get("version", 1))

    @classmethod
    def load(cls, path: str | Path | None = None) -> KoppenPriorStore:
        p = Path(path) if path is not None else _DEFAULT_PATH
        with p.open(encoding="utf-8") as fh:
            return cls(json.load(fh))

    @property
    def zones(self) -> list[str]:
        return sorted(self._data.get("zones", {}).keys())

    def resolve_zone(self, zone: str, lat: float, lon: float = 0.0) -> str:
        z = str(zone).strip()
        if z.upper() in ("", "AUTO", "DEFAULT"):
            return infer_koppen_zone(lat, lon)
        if z in self._data.get("zones", {}):
            return z
        return infer_koppen_zone(lat, lon)

    def variable_prior(
        self,
        zone: str,
        season: int,
        variable: str,
        *,
        lat: float = 45.0,
        lon: float = 0.0,
    ) -> VarPrior | None:
        z = self.resolve_zone(zone, lat, lon)
        seasons = self._data.get("zones", {}).get(z, {}).get("seasons", {})
        entry = seasons.get(str(int(season)), {})
        stats = entry.get(variable)
        if not stats:
            return None
        return VarPrior(mean=float(stats["mean"]), std=float(stats.get("std", 1.0)))

    def season_for_cluster(self, cluster_id: int, granularity: str = "seasonal") -> int:
        """Map cluster label to meteorological season 1–4 when possible."""
        if granularity == "seasonal":
            return int(cluster_id)
        month = (
            int(cluster_id) if 1 <= int(cluster_id) <= 12 else ((int(cluster_id) - 1) // 2) % 12 + 1
        )
        from pymice.integrations.weppcliff.cluster import season_from_month

        return season_from_month(month)


def load_default_priors() -> KoppenPriorStore:
    return KoppenPriorStore.load(_DEFAULT_PATH)
