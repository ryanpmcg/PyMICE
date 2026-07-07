# PyMICE documentation

PyMICE implements **Multivariate Imputation by Chained Equations (MICE / FCS)** in Python with algorithmic alignment to the R [`mice`](https://cran.r-project.org/package=mice) reference.

## User guide

- [Install](install.md)
- [Quick start](quickstart.md)
- [Vignette walkthroughs](vignettes/index.html) — Python walkthroughs of the official R `mice` tutorials (V01–V08); start with **V1: Ad Hoc MICE**

### Vignette quick links

| # | Topic | Start here |
|---|--------|------------|
| V1 | [Ad Hoc MICE](vignettes/v01_ad_hoc_mice.html) | Recommended first tutorial |
| V2 | [Convergence & pooling](vignettes/v02_convergence_pooling.html) | Traces and `pool()` |
| V3 | [Missingness models](vignettes/v03_missingness.html) | Patterns and inspection |
| V4 | [Passive imputation](vignettes/v04_passive.html) | Passive & post-processing |
| V5 | [Multilevel data](vignettes/v05_multilevel.html) | Clustered imputation |
| V6 | [Sensitivity analysis](vignettes/v06_sensitivity.html) | δ adjustment & survival |
| V7 | [Ampute (appendix)](vignettes/v07_ampute.html) | Simulate missingness |
| V8 | [Parallel MICE (appendix)](vignettes/v08_futuremice.html) | `futuremice` workflow |

Full parity table, learning path, and pytest status: [vignettes/index.html](vignettes/index.html).
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

Published site: [ryanpmcg.github.io/PyMICE](https://ryanpmcg.github.io/PyMICE/) (MkDocs + vignette HTML under `/vignettes/`).