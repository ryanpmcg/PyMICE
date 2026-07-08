# PyMICE

[![CI/CD](https://github.com/ryanpmcg/PyMICE/actions/workflows/ci.yml/badge.svg)](https://github.com/ryanpmcg/PyMICE/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-ryanpmcg.github.io%2FPyMICE-blue)](https://ryanpmcg.github.io/PyMICE/)
[![PyPI](https://img.shields.io/pypi/v/pymice-fcs)](https://pypi.org/project/pymice-fcs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Multivariate Imputation by Chained Equations (MICE / FCS)** for Python — a clean-room implementation aligned with the R [`mice`](https://cran.r-project.org/package=mice) reference, designed for statistical inference and eventual integration with [WEPPCLIFF](https://github.com/ryanpmcg/WEPPCLIFF).

## Status

**Version 0.1.0 — publication-ready (July 2026)**

| Verification | Result |
|--------------|--------|
| Unit & integration tests | 262 tests (`pytest`) |
| Vignette structural alignment (V01–V08) | 0 errors / 0 warnings |
| RNG chain parity (V01–V05) | 27/27 steps match |
| R `methods(mice)` imputation surface | 35 methods registered; 0 gaps |
| Vignette walkthrough reports | All eight vignettes run clean (`run_all.sh`) |

Algorithmic equivalence with R `mice` is validated under independent RNG (`rng="numpy"`, default). Bit-for-bit imputation parity is optional via `rng="r"` and documented optional R backends. Remaining differences are cosmetic (matplotlib vs lattice) or documented tolerances — see [`docs/dev/PARITY_STATUS.md`](docs/dev/PARITY_STATUS.md).

## Install

```bash
pip install pymice-fcs
```

Optional extras:

```bash
pip install pymice-fcs[pandas]     # DataFrame API, parallel chunking
pip install pymice-fcs[plot]       # Diagnostic plots (matplotlib)
pip install pymice-fcs[ml]         # lasso.* / lda (scikit-learn)
pip install pymice-fcs[survival]   # Cox PH pooling (lifelines)
pip install pymice-fcs[dev]        # pytest, ruff, coverage
```

The PyPI distribution is **`pymice-fcs`** (import as `pymice`). This avoids name collisions with unrelated packages [`pymice`](https://pypi.org/project/pymice/) (lab-mice behavioral data) and [`mice`](https://pypi.org/project/mice/) (stochastic optimization).

**Runtime requirements:** Python ≥ 3.10, NumPy ≥ 1.26, SciPy ≥ 1.11.

## Quick start

```python
import pymice
from pymice import mice, complete, with_mids, pool, summary_pool

# Bundled incomplete dataset (R nhanes benchmark)
data, names = pymice.load_nhanes()

# Default: PMM, m=5, maxit=5, NumPy PCG64 RNG
imp = mice(data, column_names=names, seed=123)

# Pooled linear model (Rubin 1987 + Barnard–Rubin df)
fit = with_mids(imp, formula="bmi ~ age + hyp + chl")
print(summary_pool(pool(fit)))
```

**R-aligned imputations** (requires `Rscript` + CRAN `mice`):

```python
imp_r = mice(data, column_names=names, seed=123, rng="r")
```

**Parallel imputation** (R `futuremice` workflow):

```python
from pymice import futuremice

imp_par = futuremice(data, column_names=names, m=5, parallelseed=123, n_core=2, print=False)
```

See [`docs/dev/REPRODUCIBILITY.md`](docs/dev/REPRODUCIBILITY.md) for RNG backends and publication reporting guidance.

## Features

- **FCS / Gibbs sampler** — visit sequence, predictor matrix, blocks, passive `~ I(...)`, `post` hooks
- **35 imputation methods** — full R `methods(mice)` surface including multilevel (`2l.*`), JOMO (`jomoImpute`), sensitivity (`mnar`, `ri`), and `ampute` simulation
- **Pooling** — `mira` / `mipo`, Rubin rules, `anova()`, scalar pooling (`D1`–`D3`)
- **Diagnostics** — `md.pattern()`, `flux()`, convergence and density plots
- **Parallel chains** — `futuremice()`, `parallel_mice()`, `mice(n_jobs=N)`
- **Survival** — `leiden_coxph()` + pooled Cox summaries (optional `lifelines`)
- **Pluggable RNG** — `"numpy"` (default), `"legacy"`, `"r"`, or custom `numpy.random.Generator`
- **Optional R backends** — `2l.pan`, `2l.lmer`/`2l.bin`, `ampute` (auto-detect when R packages available)

### Imputation methods

`pmm`, `norm`, `norm.nob`, `norm.boot`, `norm.predict`, `mean`, `sample`, `midastouch`, `logreg`, `logreg.boot`, `polyreg`, `polr`, `cart`, `rf`, `lda`, `quadratic`, `micemean`, `mnar`, `ri`, `2l.norm`, `2l.pan`, `2l.lmer`, `2l.bin`, `2lonly.mean`, `2lonly.norm`, `2lonly.pmm`, `jomoImpute`, `panImpute`, `jomo2con`, `jomo2ran`, `lasso.norm`, `lasso.logreg`, `lasso.select.norm`, `lasso.select.logreg`, `2logreg`

Passive formulas (`"~ I(wgt / (hgt/100)^2)"`) and multivariate blocks (`jomoImpute`, `panImpute`) are supported.

### Optional backends

| Feature | Environment variable | When active |
|---------|---------------------|-------------|
| R RNG stream | `rng="r"` | Bit-identical PMM/norm on isolated calls |
| `2l.pan` | `PYMICE_R_PAN` (auto) | R `pan::pan` Fortran sampler |
| `2l.lmer` / `2l.bin` | `PYMICE_R_LMER` (auto) | R `mice` + `lme4` |
| `lasso.*` / `lda` | `PYMICE_SKLEARN` (auto) | scikit-learn when `[ml]` installed |
| `ampute` | `PYMICE_R_AMPUTE` (auto) | R `mice::ampute` chain |

Set any flag to `0` to force the NumPy/Python fallback.

## Why this project exists

The R [`mice`](https://cran.r-project.org/package=mice) package (van Buuren & Groothuis-Oudshoorn, 2011) is the reference implementation of MICE/FCS. This repository delivers a **standalone, MIT-licensed** Python library with minimal dependencies (NumPy + SciPy core), suitable for statistical inference workflows that previously depended on R-only tooling.

## Documentation

| Document | Purpose |
|----------|---------|
| [ryanpmcg.github.io/PyMICE](https://ryanpmcg.github.io/PyMICE/) | Published docs + [vignette walkthroughs](https://ryanpmcg.github.io/PyMICE/vignettes/) |
| [`docs/index.md`](docs/index.md) | User documentation source (MkDocs) |
| [`docs/dev/PUBLICATION.md`](docs/dev/PUBLICATION.md) | PyPI release checklist, citation, reporting guidance |
| [`docs/dev/PARITY_STATUS.md`](docs/dev/PARITY_STATUS.md) | R vignette parity accomplishments and remaining gaps |
| [`docs/dev/REPRODUCIBILITY.md`](docs/dev/REPRODUCIBILITY.md) | RNG backends and cross-language validation |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Contributor workflow and verification gates |
| [`devtools/README.md`](devtools/README.md) | Vignette report generator (dev only) |
| [`reference/README.md`](reference/README.md) | R tutorial snapshots for golden tests |
| [`Paper/paper.md`](Paper/paper.md) | JOSS-style software paper draft |

## Theoretical foundation

- van Buuren, S., & Groothuis-Oudshoorn, K. (2011). *mice: Multivariate Imputation by Chained Equations in R.* JSS 45(3). [doi:10.18637/jss.v045.i03](https://doi.org/10.18637/jss.v045.i03)
- van Buuren, S. (2018). *Flexible Imputation of Missing Data* (2nd ed.). [doi:10.1201/9780429492259](https://doi.org/10.1201/9780429492259)

## Citation

If you use PyMICE in research, please cite the MICE methodology (above) and this software:

```bibtex
@software{pymice2026,
  author  = {McGehee, Ryan P.},
  title   = {PyMICE: Multivariate Imputation by Chained Equations for Python},
  year    = {2026},
  url     = {https://github.com/ryanpmcg/PyMICE},
  version = {0.1.0},
  note    = {PyPI package pymice-fcs; import as pymice}
}
```

## Repository layout

| Path | Purpose |
|------|---------|
| `src/pymice/` | Installable package |
| `tests/` | Unit tests + R golden parity |
| `docs/` | User docs (`docs/dev/` for parity and publication) |
| `reference/` | R tutorial snapshots (not shipped in wheel) |
| `Reference/` | R `mice` source snapshots (GPL, dev only) |
| `devtools/` | Vignette report generator (not shipped) |
| `Paper/` | Software paper draft |

## Development

### macOS / Linux

```bash
cd PyMICE
make check              # lint + unit tests + structural parity
# or full gate (needs R):
make check-full
```

Manual setup:

```bash
bash devtools/setup_venv.sh
source ~/.venvs/brain-pymice/bin/activate   # outside Google Drive
pytest
python devtools/maintain_parity.py
python devtools/run_vignettes.py --only 07
open docs/vignettes/index.html
make pages    # MkDocs site/ preview (includes vignettes/)
```

### Windows

```powershell
cd PyMICE
python -m venv $env:USERPROFILE\.venvs\brain-pymice
$env:USERPROFILE\.venvs\brain-pymice\Scripts\activate
python -m pip install -e ".[dev,plot,pandas,ml,survival,docs]"
pytest
python devtools\run_vignettes.py
```

### CI/CD

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on pushes and pull requests that touch PyMICE code (`src/`, `tests/`, `reference/`, `devtools/`, `pyproject.toml`, or CI workflow files). Docs-only commits skip CI.

| Job | What it verifies |
|-----|------------------|
| `lint` | Ruff format/lint, GPL contamination policy |
| `test` | Python-only pytest (`-m "not r_backend"`) + structural alignment on **Ubuntu, macOS, Windows** × Python 3.10–3.12 |
| `r-smoke` | Ubuntu + CRAN `mice`/`pan`: R RNG stream and `mice(..., rng="r")` smoke tests |
| `build` | Wheel/sdist build and Linux smoke install |
| `install-smoke` | Wheel-only install on Ubuntu, macOS, and Windows (no source tree) |

Full R chain parity (RNG + `maintain_parity.py`) runs nightly via [`.github/workflows/parity-nightly.yml`](.github/workflows/parity-nightly.yml).

### GitHub Pages

[`.github/workflows/pages.yml`](.github/workflows/pages.yml) publishes [ryanpmcg.github.io/PyMICE](https://ryanpmcg.github.io/PyMICE/) when `docs/` (including `docs/vignettes/`), `mkdocs.yml`, or the Pages workflow changes. Deployment requires a green CI/CD run on `main`—either from the same push (code + docs) or the latest successful CI on the branch (docs-only). One-time: repo **Settings → Pages → Build and deployment → GitHub Actions**. Regenerate and commit `docs/vignettes/` after vignette changes (`make vignettes`).

## License

- **Python package (`src/pymice/`):** MIT — see [`LICENSE`](LICENSE)
- **Reference R snapshots (`Reference/`):** GPL-2|GPL-3 (upstream `mice`); development reference only, not distributed in the wheel
- **R tutorial snapshots (`reference/`):** third-party tutorial material; see [`docs/dev/ATTRIBUTION.md`](docs/dev/ATTRIBUTION.md)