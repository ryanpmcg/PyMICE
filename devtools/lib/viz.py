"""Save matplotlib figures for vignette reports."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


def save_figure(fig, assets_dir: Path, filename: str, *, dpi: int = 120) -> Path:
    assets_dir.mkdir(parents=True, exist_ok=True)
    path = assets_dir / filename
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return path
