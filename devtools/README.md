# devtools (development only)

This folder is **not published** with the `pymice` wheel. It runs PyMICE vignette demonstrations inside a dedicated virtual environment and writes viewable HTML/Markdown reports.

## Quick start

From the repository root:

```bash
bash devtools/run_all.sh
open docs/vignettes/index.html
```

Or step by step:

```bash
bash devtools/setup_venv.sh
source ~/.venvs/brain-pymice/bin/activate   # outside Drive; override: PYMICE_VENV
pytest                                    # 262 tests
python devtools/maintain_parity.py        # structural + RNG audits
python devtools/run_vignettes.py          # eight vignette reports → docs/vignettes/
```

**Venv:** `~/.venvs/brain-pymice` (never `devtools/.venv` — Drive cannot exclude it). See Brain `Scripts/README.md`.

Vignettes use `rng="r"` for R-matching imputations. On first run, `run_vignettes.py` checks for R and installs `mice`/`pan` automatically when missing (via bundled `pymice/scripts/install_r.sh`). Set `PYMICE_SKIP_R_INSTALL=1` to disable auto-install.

## What it does

1. **`setup_venv.sh`** — creates `~/.venvs/brain-pymice` and installs `pymice[dev,plot,pandas,ml,survival,docs]`.
2. **`run_vignettes.py`** — runs eight vignette demos (aligned with `reference/01`–`08`), captures tables/plots.
3. **`maintain_parity.py`** — runs `audit_vignette_alignment.py` + `audit_rng_parity.py`; refreshes `parity_backlog.json`.
4. **Publish** — writes `docs/vignettes/` (HTML/MD + `assets/`); deployed at [ryanpmcg.github.io/PyMICE/vignettes/](https://ryanpmcg.github.io/PyMICE/vignettes/) via GitHub Pages.

## Publication verification

Before a PyPI release, run the full gate from [`docs/dev/PUBLICATION.md`](../docs/dev/PUBLICATION.md):

```bash
source ~/.venvs/brain-pymice/bin/activate
pytest
python devtools/maintain_parity.py    # expect 27/27 RNG match, 0 alignment errors
python devtools/run_vignettes.py      # expect V01–V08 ok
```

## R vignette parity

Each vignette runner mirrors the exercises from [gerkovink.com/miceVignettes](https://www.gerkovink.com/micereference/).

All eight vignettes use the full tutorial layout:

- Original R **introduction** and **numbered section titles**
- **Part headings** where the R tutorial has them
- **Narrative prose** before/after code blocks (`devtools/lib/v0N_narrative.py`)
- Per executable block: **R code** → **Python code** → **formatted output**
- **Parity badges** — ✅ match, ⚠️ partial, ⏭️ skip (R-only), ❌ mismatch

Parity accomplishments: [`docs/dev/PARITY_STATUS.md`](../docs/dev/PARITY_STATUS.md). Post-release queue: [`docs/dev/PARITY_IMPLEMENTATION_PLAN.md`](../docs/dev/PARITY_IMPLEMENTATION_PLAN.md).

Golden text comes from `reference/*/golden_outputs.json` and `vignette_extracted.R`. Refresh chain-aligned goldens:

| Script | Scope |
|--------|-------|
| `regenerate_draw_order_goldens.py` | V02–V04 draw-order steps |
| `regenerate_v05_goldens.py` | V05 step 16 (`head(complete(imp2))`) |
| `regenerate_v06_goldens.py` | V06 steps 11–13 (Cox/pool/δ qbar) |
| `maintain_parity.py` | Structural + RNG re-compare; updates `parity_backlog.json` |

Export reference datasets first (requires R + network):

```bash
bash reference/export_vignette_datasets.sh
```

| # | R vignette | PyMICE coverage |
|---|------------|-----------------|
| 01 | Ad hoc and MICE | Steps **1–14**; chain-aligned PMM/norm with `rng="r"` |
| 02 | Convergence and pooling | Steps **1–8**; mira/pool exact (goldens refreshed 2026-07) |
| 03 | Missingness inspection | Steps **1–15**; boys + mammalsleep pool chains |
| 04 | Passive imputation | Steps **1–9**; passive BMI, post_squeeze on `tv` |
| 05 | Multilevel | Steps **1–26**; setup exact; sampler diagnostics ~0.15 tolerance |
| 06 | Sensitivity | Steps **1–13**; Cox/pool/qbar exact; δ chains |
| 07 | ampute | Steps **1–11** + reference step 12; R backend exact |
| 08 | futuremice | Steps **1–8**; `parallelseed` reproducible; benchmarks skipped |

## Layout

```
devtools/
├── setup_venv.sh           # create .venv + install pymice[dev,plot,...]
├── run_all.sh              # setup + run_vignettes.py
├── run_vignettes.py        # orchestrator
├── maintain_parity.py      # structural + RNG audit wrapper
├── audit_vignette_alignment.py
├── audit_rng_parity.py
├── parity_backlog.json
├── lib/                    # report helpers, chain RNG, parity docs
├── runners/                # one runner per vignette
└── output/                 # generated reports (gitignored)
```

## Regenerating R goldens (optional)

Vignette tests that compare to R still use `tests/goldens/r/`. Refresh with:

```bash
bash tests/run_r_goldens.sh
```