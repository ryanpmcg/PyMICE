# Contributing to PyMICE

Thank you for improving PyMICE. This project pairs a **published Python package** (`src/pymice/`) with **devtools** used to validate alignment against R `mice` tutorials.

## Quick verification

```bash
make check          # lint + unit tests + structural parity (no R chains)
make check-full     # adds RNG parity + full vignette reports (needs R)
```

Or manually:

```bash
bash devtools/setup_venv.sh
source ~/.venvs/brain-pymice/bin/activate
pytest
pytest tests/parity/test_structural_alignment.py
python devtools/maintain_parity.py   # structural + RNG audits (R required for RNG)
```

## Repository layout

| Path | Purpose |
|------|---------|
| `src/pymice/` | Installable library (shipped on PyPI) |
| `tests/` | Unit tests and parity pytest modules |
| `reference/` | Frozen R tutorial snapshots (`golden_outputs.json`) |
| `devtools/` | Vignette runners, audits, HTML reports (not shipped) |
| `docs/` | User documentation (MkDocs); `docs/vignettes/` published on GitHub Pages |
| `docs/dev/` | Maintainer parity and publication docs |

## Refreshing R goldens

After R or chain changes, refresh affected snapshots **with provenance**:

```bash
python devtools/refresh_goldens.py --vignette 05,07
# or
python devtools/refresh_goldens.py --all
```

Each `golden_outputs.json` gains/updates a `_provenance` block (R version, `mice` version, timestamp).

## Continuous integration

GitHub Actions (`.github/workflows/ci.yml`) mirrors local `make check` on every PR:

- **lint** — `ruff format --check`, `ruff check`, GPL policy on `src/pymice/`
- **test** — `pytest` (excluding RNG parity) + structural alignment on Ubuntu, macOS, and Windows with Python 3.10–3.12
- **build** / **install-smoke** — wheel build and install-from-wheel on all three OS families

RNG chain parity and the full `maintain_parity.py` audit run nightly (`.github/workflows/parity-nightly.yml`; needs R). Refresh goldens locally before merging parity-sensitive changes.

## Pull requests

1. Run `make check` before opening a PR (CI will run the same gates cross-platform).
2. Note whether parity-sensitive steps changed; refresh goldens if needed.
3. Keep algorithm changes in `src/pymice/` separate from report formatting in `devtools/lib/`.

## Code style

- Ruff for format and lint (`ruff format .`, `ruff check .`)
- Match existing naming and import style in touched modules