"""EI / I30 proxy validation gates for imputed storm sequences."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class EIValidationResult:
    passed: bool
    i30_imputed: float = 0.0
    i30_donor_median: float = 0.0
    ratio: float = 1.0
    warnings: list[str] = field(default_factory=list)

    def summary_lines(self) -> list[str]:
        status = "PASS" if self.passed else "WARN"
        lines = [
            f"EI/I30 validation: {status}",
            f"  imputed I30 proxy: {self.i30_imputed:.3f}",
            f"  donor median I30:   {self.i30_donor_median:.3f}",
            f"  ratio:              {self.ratio:.3f}",
        ]
        lines.extend(f"  - {w}" for w in self.warnings)
        return lines


def i30_proxy(
    df: pd.DataFrame,
    *,
    window_min: float = 30.0,
) -> float:
    """
    Maximum 30-minute depth proxy (mm per 30 min) on a breakpoint sequence.

    Mirrors WEPPCLIFF ``int_30m`` intent without ``smart_window_sum`` dependency.
    """
    if df.empty or "PRECIP" not in df.columns or "DUR" not in df.columns:
        return 0.0

    work = df.sort_values("DT_1").copy()
    work["DT_1"] = pd.to_datetime(work["DT_1"])
    t0 = work["DT_1"].iloc[0]
    minutes = (work["DT_1"] - t0).dt.total_seconds() / 60.0
    durs = work["DUR"].astype(float).to_numpy()
    prec = work["PRECIP"].astype(float).to_numpy()

    best = 0.0
    for i in range(len(work)):
        end = float(minutes.iloc[i]) + float(durs[i])
        j = i
        depth = 0.0
        while j < len(work) and float(minutes.iloc[j]) < end:
            depth += float(prec[j])
            j += 1
        span = max(end - float(minutes.iloc[i]), 1e-6)
        rate = depth * (window_min / span)
        best = max(best, rate)
    return float(best)


def validate_i30_against_donors(
    imputed_day: pd.DataFrame,
    donor_days: list[pd.DataFrame],
    *,
    min_ratio: float = 0.5,
) -> EIValidationResult:
    """Gate imputed sustained intensity against donor pool."""
    i30_imp = i30_proxy(imputed_day)
    donor_i30 = [i30_proxy(d) for d in donor_days if not d.empty]
    med = float(np.median(donor_i30)) if donor_i30 else i30_imp
    ratio = i30_imp / med if med > 1e-9 else 1.0
    warnings: list[str] = []
    passed = True
    if donor_i30 and ratio < min_ratio:
        passed = False
        warnings.append(
            f"imputed I30 proxy {i30_imp:.2f} is {ratio:.0%} of donor median {med:.2f} "
            f"(threshold {min_ratio:.0%})"
        )
    return EIValidationResult(
        passed=passed,
        i30_imputed=i30_imp,
        i30_donor_median=med,
        ratio=ratio,
        warnings=warnings,
    )
