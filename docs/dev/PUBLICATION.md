# PyMICE — Publication and release guide

Last updated: 2026-07-05

This document is the single checklist for publishing **PyMICE 0.1.0** to PyPI and citing it in research.

---

## Release readiness (0.1.0)

| Gate | Status | Command |
|------|--------|---------|
| Unit tests | ✅ 262 collected | `pytest` |
| Vignette reports | ✅ V01–V08 | `bash devtools/run_all.sh` |
| Structural alignment | ✅ 0 errors / 0 warnings | `python devtools/audit_vignette_alignment.py` |
| RNG chain parity | ✅ 27/27 | `python devtools/maintain_parity.py` |
| R method surface | ✅ 35 registered, 0 gaps | `pytest tests/unit/test_r_gaps_implemented.py` |
| License & attribution | ✅ MIT + ATTRIBUTION.md | manual review |
| Optional extras install | ✅ `[pandas,plot,ml,survival,dev]` | `pip install -e ".[dev,plot,pandas,ml,survival]"` |

Remaining parity gaps (P1–P2 in [`PARITY_STATUS.md`](PARITY_STATUS.md)) are **non-blocking** for publication: cosmetic rendering, optional RNG paths, and documented sampler tolerances.

---

## GitHub Pages (docs + vignettes)

| URL | Content |
|-----|---------|
| https://ryanpmcg.github.io/PyMICE/ | MkDocs user guide |
| https://ryanpmcg.github.io/PyMICE/vignettes/ | R-aligned walkthrough reports (V01–V08) |

1. **One-time:** GitHub repo → Settings → Pages → Build and deployment → **GitHub Actions**.
2. **Deploy:** push to `main` runs the `pages` job in `.github/workflows/ci.yml` (after `lint`, `test`, and `build` pass).
3. **Refresh vignettes:** `make vignettes` (needs R), commit `docs/vignettes/`, push.

### CI/CD pipeline

| Workflow | Trigger | Coverage |
|----------|---------|----------|
| `ci.yml` | push/PR to `main`, `workflow_dispatch` | Lint, cross-platform tests (3 OS × Python 3.10–3.12), wheel build, install smoke, Pages deploy |
| `parity-nightly.yml` | daily cron, `workflow_dispatch` | R-backed structural + RNG parity, `maintain_parity.py` |

---

## PyPI release procedure

### 1. Pre-release checks

```bash
cd PyMICE
source ~/.venvs/brain-pymice/bin/activate

pytest
python devtools/maintain_parity.py
python devtools/run_vignettes.py   # all eight vignettes → ok
ruff check src/pymice tests
```

### 2. Build artifacts

```bash
pip install build twine
python -m build
```

Inspect `dist/pymice-0.1.0-py3-none-any.whl` — confirm `devtools/` is excluded and R helper scripts are bundled under `pymice/methods/`.

### 3. Configure PyPI authentication (one-time)

**Preferred — GitHub trusted publishing** (no stored tokens):

1. Sign in at [pypi.org](https://pypi.org/) → **Account settings** → **Publishing** → **Add a new pending publisher**
2. Set:
   - **PyPI project name:** `pymice-fcs`
   - **Owner:** `ryanpmcg`
   - **Repository name:** `PyMICE`
   - **Workflow name:** `publish.yml`
   - **Environment name:** *(leave blank)*
3. Save. The project is created on first successful upload.

**Alternative — API token:** create a PyPI token scoped to `pymice-fcs` and add it as the GitHub repository secret `PYPI_API_TOKEN`.

### 4. Publish via GitHub Actions

```bash
# Tag is already v0.1.0; re-run after trusted publisher is configured:
# GitHub → Actions → Publish to PyPI → Run workflow
```

Or publish a GitHub Release (`v0.1.0`) — the workflow also runs on `release: published`.

### 5. Local upload (optional)

```bash
twine upload dist/*
# Username: __token__   Password: <PyPI API token>
```

### 6. Post-release

- Tag `v0.1.0` on GitHub
- Update `Paper/paper.md` date if submitting to JOSS
- Announce with citation block from [`README.md`](../README.md)

---

## What to report in papers

When describing PyMICE results:

1. **Software** — `pymice` version, Python version, optional extras (`lifelines`, `scikit-learn`).
2. **MICE settings** — `m`, `maxit`, imputation methods per variable, visit sequence if non-default.
3. **RNG** — `rng` backend (`"numpy"` default vs `"r"` for R-matching). Do not claim R-identical imputations unless `rng="r"` (and chain order matches, where relevant).
4. **Pooling** — Rubin (1987) rules with Barnard–Rubin (1999) degrees of freedom; report pooled estimates and SEs, not single completed datasets.
5. **Comparison to R** — Prefer pooled coefficients, FMI, and diagnostic shapes over cell-level imputation tables unless deterministic methods or `rng="r"` are used.

Full guidance: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

---

## Citing PyMICE

**Methodology (required):**

- van Buuren, S., & Groothuis-Oudshoorn, K. (2011). *mice: Multivariate Imputation by Chained Equations in R.* JSS 45(3). https://doi.org/10.18637/jss.v045.i03
- Rubin, D. B. (1987). *Multiple Imputation for Nonresponse in Surveys.* Wiley.

**Software (this package):**

```bibtex
@software{pymice2026,
  author  = {McGehee, Ryan P.},
  title   = {PyMICE: Multivariate Imputation by Chained Equations for Python},
  year    = {2026},
  url     = {https://github.com/ryanpmcg/PyMICE},
  version = {0.1.0}
}
```

JOSS draft: [`Paper/paper.md`](../Paper/paper.md).

---

## Known limitations (disclose in methods sections)

| Topic | Limitation |
|-------|------------|
| Default RNG | NumPy PCG64; imputations differ from R unless `rng="r"` |
| Diagnostic plots | matplotlib equivalents; not pixel-identical to R lattice |
| Multilevel samplers | `2l.norm` / `2l.pan` moments within ~0.15 of R on V05; optional R backends for `2l.pan`, `2l.lmer`, `2l.bin` |
| Native ampute | Slight drift vs older R 4.5.2 goldens; R backend exact |
| V08 benchmarks | Wall-clock timing figures are R-only (skipped in PyMICE walkthrough) |
| Factor labels | `summary()` / `str()` may show numeric codes vs R factor labels |

---

## Support files shipped in the wheel

| Asset | Purpose |
|-------|---------|
| `pymice/data/*.csv` | Bundled benchmark datasets |
| `pymice/methods/r_rng_server.R` | R RNG subprocess (`rng="r"`) |
| `pymice/methods/r_pan_impute.R` | Optional `2l.pan` backend |
| `pymice/methods/r_lme4_impute.R` | Optional `2l.lmer` / `2l.bin` backend |
| `pymice/methods/r_ampute.R` | Optional `ampute` backend |
| `pymice/scripts/install_r.sh` | R prerequisite installer |

`devtools/`, `reference/`, and `Reference/` are **not** distributed on PyPI.

---

## Maintenance after release

```bash
python devtools/maintain_parity.py          # after chain or golden changes
python devtools/regenerate_v06_goldens.py   # after Cox/δ chain changes
pytest tests/vignettes/ -q
```

Active non-blocking queue: [`PARITY_IMPLEMENTATION_PLAN.md`](PARITY_IMPLEMENTATION_PLAN.md).