# Changelog

All notable changes to PyMICE are documented here. The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- Venv relocated to `~/.venvs/brain-pymice` (outside Google Drive); legacy `devtools/.venv` deprecated
- Vignette reports publish to `docs/vignettes/` and deploy at `ryanpmcg.github.io/PyMICE/vignettes/`
- Repository layout: `Vignettes/` → `reference/`, `Commands/` → `devtools/`, runners in `devtools/runners/`
- Maintainer docs moved to `docs/dev/`; user docs in `docs/` (MkDocs)
- Unified golden refresh: `python devtools/refresh_goldens.py`
- CI/CD consolidated into `.github/workflows/ci.yml`: lint, cross-platform tests (Ubuntu/macOS/Windows × Python 3.10–3.12), wheel build, install smoke, and GitHub Pages deploy; RNG parity nightly in `parity-nightly.yml`
- Public docs and package metadata point to `https://ryanpmcg.github.io/PyMICE/` and `github.com/ryanpmcg/PyMICE` (repo name matches GitHub `PyMICE`)

### Fixed

- `load_nhanes()` returns a copy so in-place test mutations cannot corrupt cached data

## [0.1.0] — 2026-07-05

First public release. Publication-ready algorithmic parity with R `mice` 3.19 under independent RNG.

### Added

- Full FCS / Gibbs sampler (`mice`, `continue_imputation`, visit sequence, blocks, passive/post)
- 35 imputation methods covering the complete R `methods(mice)` surface
- Rubin pooling (`pool`, `summary_pool`, `anova`, `mira` workflow via `with_mids`)
- Pluggable RNG: `"numpy"` (default), `"legacy"`, `"r"`, custom `Generator`
- Parallel imputation: `futuremice`, `parallel_mice`, `mice(n_jobs=N)`
- Missingness simulation: native `ampute` + optional R backend
- Multilevel imputation: `2l.norm`, `2l.pan`, `2l.lmer`, `2l.bin`, `2lonly.*`
- Multivariate JOMO: `jomoImpute`, `panImpute`, `jomo2con`, `jomo2ran`
- Survival sensitivity: `leiden_coxph`, δ-adjustment chains (V06)
- Diagnostics: `md.pattern`, `flux`, matplotlib plot dispatch
- Bundled datasets: `nhanes`, `boys`, `mammalsleep`, `popNCR*`, `leiden`
- Optional R backends: `2l.pan`, `2l.lmer`/`2l.bin`, `ampute` (auto-detect)
- Optional scikit-learn backend: `lasso.*`, `lda` (auto-detect with `[ml]`)
- Mids utilities: `as_mids`, `cbind_mids`, `rbind_mids`, `ibind`
- WEPPCLIFF integration adapter (`pymice.integrations.weppcliff`)

### Verified

- 262 unit and integration tests
- Eight R vignette walkthroughs (V01–V08): structural alignment 0 errors / 0 warnings
- RNG chain parity: 27/27 steps (V01–V05)
- V06 Cox/pool/qbar exact; V08 `futuremice` + `parallelseed` reproducible

### Fixed

- `futuremice(print=False)` no longer crashes when auto-selecting worker count (builtin `print` shadowing)
- Wheel build: removed duplicate `force-include` entries that conflicted with package data files

### Documentation

- Publication guide (`docs/dev/PUBLICATION.md`)
- Parity status and implementation plan (V01–V08)
- Reproducibility and attribution guides
- JOSS-style software paper draft (`Paper/paper.md`)