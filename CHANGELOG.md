# Changelog

All notable changes to PyMICE are documented here. The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- Venv relocated to `~/.venvs/brain-pymice` (outside Google Drive); `setup_venv.sh` auto-removes legacy `devtools/.venv`
- Vignette reports publish to `docs/vignettes/` and deploy at `ryanpmcg.github.io/PyMICE/vignettes/`
- Repository layout: `Vignettes/` → `reference/`, `Commands/` → `devtools/`, runners in `devtools/runners/`
- Maintainer docs moved to `docs/dev/`; user docs in `docs/` (MkDocs)
- Unified golden refresh: `python devtools/refresh_goldens.py`
- CI/CD consolidated into `.github/workflows/ci.yml`: lint, cross-platform tests (Ubuntu/macOS/Windows × Python 3.10–3.12), wheel build, install smoke, and GitHub Pages deploy; RNG parity nightly in `parity-nightly.yml`
- Public docs and package metadata point to `https://ryanpmcg.github.io/PyMICE/` and `github.com/ryanpmcg/PyMICE` (repo name matches GitHub `PyMICE`)

### Fixed

- `load_nhanes()` returns a copy so in-place test mutations cannot corrupt cached data
