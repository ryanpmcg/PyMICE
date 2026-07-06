# PyMICE documentation

PyMICE implements **Multivariate Imputation by Chained Equations (MICE / FCS)** in Python with algorithmic alignment to the R [`mice`](https://cran.r-project.org/package=mice) reference.

## User guide

- [Install](install.md)
- [Quick start](quickstart.md)
- [Vignette walkthroughs](vignettes/index.html) — R-aligned tutorial reports (V01–V08)
- [Citing PyMICE](citing.md)

## Maintainer / parity

Development tooling, R golden snapshots, and parity status live under [dev/](dev/PARITY_STATUS.md).

## Package reference

API documentation is generated from docstrings. Build locally:

```bash
bash devtools/setup_venv.sh
source ~/.venvs/brain-pymice/bin/activate
pip install -e ".[dev,docs]"
mkdocs serve
```

Published site: [ryanpmcg.github.io/pymice](https://ryanpmcg.github.io/pymice/) (MkDocs + vignette HTML under `/vignettes/`).