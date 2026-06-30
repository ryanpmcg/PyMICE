# Commands (development only)

This folder is **not published** with the `pymice` wheel. It runs PyMICE vignette demonstrations and the test suite inside a dedicated virtual environment, then writes viewable reports.

## Quick start

From the repository root:

```bash
bash Commands/run_all.sh
open Commands/output/index.html
```

Or step by step:

```bash
bash Commands/setup_venv.sh
source Commands/.venv/bin/activate
python Commands/run_vignettes.py
```

## What it does

1. **`setup_venv.sh`** — creates `Commands/.venv` and installs `pymice` in editable mode with `[dev,plot]` extras.
2. **`run_vignettes.py`** — runs eight vignette demos (aligned with `Vignettes/01`–`08`), captures tables/plots, and runs `pytest tests/`.
3. **Output** — writes `Commands/output/index.html`, per-vignette `.html`/`.md` files, and `assets/` figures.

## R vignette parity

Each vignette runner mirrors the exercises from [gerkovink.com/miceVignettes](https://www.gerkovink.com/miceVignettes/).

**Vignettes 01–04** use the full tutorial layout:

- Original R **introduction** and **numbered section titles** (same as the HTML vignettes)
- **Part headings** where the R tutorial has them
- **Narrative prose** before/after code blocks (from `Commands/lib/v0N_narrative.py`)
- Per executable block: **R code** → **Python code** → **formatted output**
- **Parity badges** — ✅ match, ⚠️ partial, ⏭️ skip (R-only), ❌ mismatch

**Vignettes 07–08** still use the earlier step-per-exercise layout (conversion pending).

Golden text comes from `Vignettes/*/vignette_extracted.R`. Prose is extracted with `Vignettes/extract_vignette_prose.py`.

Export reference datasets first (requires R + network):

```bash
bash Vignettes/export_vignette_datasets.sh
```

| # | R vignette | PyMICE coverage |
|---|------------|-----------------|
| 01 | Ad hoc and MICE | R-numbered steps **1–14**; intro + parts + narrative |
| 02 | Convergence and pooling | R-numbered steps **1–8**; predictor matrix, convergence, pooling |
| 03 | Missingness inspection | R-numbered steps **1–15**; boys missingness, mammalsleep pooling |
| 04 | Passive imputation | R-numbered steps **1–9**; passive `ts`, boys `bmi`, `post`/`squeeze` on `tv` |
| 05 | Multilevel | ✅ R-aligned (steps 1–26); 2l.* + JOMO/PAN (partial RNG) |
| 06 | Sensitivity | ✅ R-aligned (steps 1–13); Cox PH skipped (11–12); δ/post steps run |
| 07 | ampute | ✅ MCAR + MAR/MNAR; legacy report layout |
| 08 | futuremice | ✅ `mice()` equivalent (steps 1–6); parallel wrapper skipped (R-only) |

## Layout

```
Commands/
├── setup_venv.sh      # create .venv + install pymice[dev,plot]
├── run_all.sh         # setup + run_vignettes.py
├── run_vignettes.py   # orchestrator
├── lib/               # report helpers
├── vignettes/         # one runner per vignette
└── output/            # generated reports (gitignored)
```

## Regenerating R goldens (optional)

Vignette tests that compare to R still use `tests/goldens/r/`. Refresh with:

```bash
bash tests/run_r_goldens.sh
```