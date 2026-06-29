"""Imputation diagnostics for WEPPCLIFF verbose output."""

from __future__ import annotations

from dataclasses import dataclass, field

from pymice.integrations.weppcliff.missingness import MissingnessProfile


@dataclass
class ImputationReport:
    granularity: str = ""
    koppen_zone: str = ""
    prior_weight: float = 0.0
    strategies: list[str] = field(default_factory=list)
    missingness: MissingnessProfile | None = None
    n_imputed_cells: int = 0
    nonstationary: bool = False

    def summary_lines(self) -> list[str]:
        lines = ["PyMICE imputation report:"]
        if self.granularity:
            lines.append(f"  cluster granularity: {self.granularity}")
        if self.koppen_zone:
            lines.append(f"  Köppen zone: {self.koppen_zone}")
        if self.nonstationary:
            lines.append("  nonstationary: year-block predictors enabled")
        if self.prior_weight > 0:
            lines.append(f"  prior blend weight (1-local): {self.prior_weight:.2f}")
        if self.missingness is not None:
            lines.append(f"  missingness: {self.missingness.primary.value}")
            if self.missingness.sparse_clusters:
                lines.append(f"  sparse clusters: {self.missingness.sparse_clusters[:8]}")
        if self.strategies:
            lines.append(f"  strategies: {', '.join(self.strategies)}")
        if self.n_imputed_cells:
            lines.append(f"  cells imputed: {self.n_imputed_cells}")
        return lines


def format_report(report: ImputationReport) -> str:
    return "\n".join(report.summary_lines())
