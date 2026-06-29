"""Storm-template donor imputation for sub-daily precipitation breakpoints."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import NDArray


@dataclass
class DayTemplate:
    """Intra-day breakpoint pattern (relative spacing + depth fractions)."""

    cluster: int
    yyyymmdd: str
    bps: int
    daily_precip: float
    offsets_min: NDArray[np.float64]
    dur: NDArray[np.float64]
    precip_frac: NDArray[np.float64]
    start_minute: float

    @property
    def feature_vector(self) -> NDArray[np.float64]:
        return np.array(
            [
                float(self.bps),
                float(self.daily_precip),
                float(self.dur.sum()),
                float(self.offsets_min[-1] if len(self.offsets_min) else 0),
            ],
            dtype=np.float64,
        )


def _minute_of_day(dt: pd.Series) -> NDArray[np.float64]:
    parsed = pd.to_datetime(dt)
    return (parsed.dt.hour * 60 + parsed.dt.minute + parsed.dt.second / 60.0).to_numpy(
        dtype=np.float64
    )


def extract_day_templates(
    ts_df: pd.DataFrame,
    *,
    dt_col: str = "DT_1",
    date_col: str = "YYYYMMDD",
    cluster_col: str = "CLUSTER",
) -> list[DayTemplate]:
    """Build donor templates from fully observed wet-day breakpoint sequences."""
    required = {dt_col, "DUR", "PRECIP", date_col, cluster_col}
    if not required.issubset(ts_df.columns):
        return []

    work = ts_df.dropna(subset=["DUR", "PRECIP", dt_col]).copy()
    if work.empty:
        return []

    work[date_col] = work[date_col].astype(str)
    work["_mod"] = _minute_of_day(work[dt_col])
    templates: list[DayTemplate] = []

    for (ymd, cluster), grp in work.groupby([date_col, cluster_col], sort=False):
        grp = grp.sort_values(dt_col)
        if grp["PRECIP"].isna().any() or grp["DUR"].isna().any():
            continue
        total = float(grp["PRECIP"].sum())
        if total <= 0:
            continue
        offsets = grp["_mod"].to_numpy(dtype=np.float64) - grp["_mod"].iloc[0]
        fracs = grp["PRECIP"].to_numpy(dtype=np.float64) / total
        templates.append(
            DayTemplate(
                cluster=int(cluster),
                yyyymmdd=str(ymd),
                bps=len(grp),
                daily_precip=total,
                offsets_min=offsets,
                dur=grp["DUR"].to_numpy(dtype=np.float64),
                precip_frac=fracs,
                start_minute=float(grp["_mod"].iloc[0]),
            )
        )
    return templates


def _resample_template(template: DayTemplate, target_bps: int) -> DayTemplate:
    n = int(max(1, target_bps))
    if template.bps == n:
        return template
    idx = np.linspace(0, template.bps - 1, n)
    idx_floor = np.floor(idx).astype(int)
    idx_ceil = np.minimum(idx_floor + 1, template.bps - 1)
    w = idx - idx_floor
    offsets = (1 - w) * template.offsets_min[idx_floor] + w * template.offsets_min[idx_ceil]
    dur = (1 - w) * template.dur[idx_floor] + w * template.dur[idx_ceil]
    frac = (1 - w) * template.precip_frac[idx_floor] + w * template.precip_frac[idx_ceil]
    s = frac.sum()
    if s > 0:
        frac = frac / s
    return DayTemplate(
        cluster=template.cluster,
        yyyymmdd=template.yyyymmdd,
        bps=n,
        daily_precip=template.daily_precip,
        offsets_min=offsets,
        dur=dur,
        precip_frac=frac,
        start_minute=template.start_minute,
    )


def select_donor_template(
    templates: list[DayTemplate],
    *,
    cluster: int,
    bps: int,
    daily_precip: float,
    rng: np.random.Generator,
    k: int = 5,
) -> DayTemplate | None:
    """PMM-style donor day selection within cluster."""
    pool = [t for t in templates if t.cluster == cluster]
    if not pool:
        pool = templates
    if not pool:
        return None

    target = np.array([float(bps), float(daily_precip), float(bps) * 5.0, 720.0], dtype=np.float64)
    feats = np.vstack([t.feature_vector for t in pool])
    scale = np.maximum(np.nanstd(feats, axis=0), 1e-6)
    dists = np.linalg.norm((feats - target) / scale, axis=1)
    order = np.argsort(dists)
    k_eff = min(k, len(order))
    pick = int(rng.choice(order[:k_eff]))
    return _resample_template(pool[pick], bps)


def apply_template_to_day(
    template: DayTemplate,
    *,
    yyyymmdd: str,
    daily_precip: float,
    bps: int,
    cluster: int,
    start_minute: float | None = None,
) -> pd.DataFrame:
    """Generate breakpoint rows for one wet day from a donor template."""
    tpl = _resample_template(template, bps)
    start = float(tpl.start_minute if start_minute is None else start_minute)
    base = pd.to_datetime(str(yyyymmdd), format="%Y%m%d")
    rows: list[dict] = []
    total_p = float(max(daily_precip, 0.0))
    for off, dur, frac in zip(tpl.offsets_min, tpl.dur, tpl.precip_frac, strict=True):
        t = base + pd.Timedelta(minutes=start + off)
        rows.append(
            {
                "DT_1": t,
                "YYYYMMDD": str(yyyymmdd),
                "CLUSTER": cluster,
                "DUR": float(max(dur, 0.1)),
                "PRECIP": float(frac * total_p),
                "HOUR": t.hour,
                "MINUTE": t.minute,
                "SECOND": t.second,
            }
        )
    return pd.DataFrame(rows)


def cluster_median_start(templates: list[DayTemplate], cluster: int) -> float:
    starts = [t.start_minute for t in templates if t.cluster == cluster]
    if not starts:
        starts = [t.start_minute for t in templates]
    return float(np.median(starts)) if starts else 720.0
