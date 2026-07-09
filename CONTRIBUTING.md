# Contributing to PyMICE

Thank you for improving PyMICE. This project pairs a **published Python package** (`src/pymice/`) with **devtools** used to validate alignment against R `mice` tutorials.

## Quick verification

```bash
make check          # lint + unit tests + structural parity (no R chains)
make check-full     # adds RNG parity + full vignette reports (needs R)
```

### Before every commit or push

CI fails fast on lint. Run this on the **whole repo** before committing Python or test changes:

```bash
ruff format --check .
ruff check .
```

Or `make lint`. Passing `pytest` alone is not sufficient. See `AGENTS.md` for agent-specific requirements.

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
- **test** — `pytest -m "not r_backend"` (no R required) + structural alignment on Ubuntu, macOS, and Windows with Python 3.10–3.12
- **r-smoke** — Ubuntu job with CRAN `mice`/`pan`: R RNG stream + `mice(..., rng="r")` smoke tests
- **build** / **install-smoke** — wheel build and install-from-wheel on all three OS families

R-marked tests (`@pytest.mark.r_backend`) are skipped in the cross-platform matrix. Full R chain parity and `maintain_parity.py` run nightly (`.github/workflows/parity-nightly.yml`). Refresh goldens locally before merging parity-sensitive changes.

## Pull requests

1. Run `make check` before opening a PR (CI will run the same gates cross-platform).
2. Note whether parity-sensitive steps changed; refresh goldens if needed.
3. Keep algorithm changes in `src/pymice/` separate from report formatting in `devtools/lib/`.

## Code style

- Ruff for format and lint — CI runs `ruff format --check .` then `ruff check .` (format first)
- Auto-fix locally: `ruff format .` then `ruff check . --fix`, then re-run both `--check` commands
- Match existing naming and import style in touched modules