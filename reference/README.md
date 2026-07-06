# Vignettes — R reference scripts for verification

This folder holds **reference material** from published `mice` tutorials. It is not part of the installable Python package; it drives parity testing against R `mice`.

## Layout

| Folder | Source | Extracted R |
|--------|--------|-------------|
| `01_ad_hoc_and_mice/` | [Ad hoc methods and mice](https://www.gerkovink.com/micereference/Ad_hoc_and_mice/Ad_hoc_methods.html) | `vignette_extracted.R` |
| `02_convergence_and_pooling/` | [Convergence and pooling](https://www.gerkovink.com/micereference/Convergence_pooling/Convergence_and_pooling.html) | `vignette_extracted.R` |
| `03_missingness_inspection/` | [Missingness inspection](https://www.gerkovink.com/micereference/Missingness_inspection/Missingness_inspection.html) | `vignette_extracted.R` |
| `04_passive_post_processing/` | [Passive imputation and post-processing](https://www.gerkovink.com/micereference/Passive_Post_processing/Passive_imputation_post_processing.html) | `vignette_extracted.R` |
| `05_multilevel_data/` | [Imputing multilevel data](https://www.gerkovink.com/micereference/Multi_level/Multi_level_data.html) | `vignette_extracted.R` |
| `06_sensitivity_analysis/` | [Sensitivity analysis](https://www.gerkovink.com/micereference/Sensitivity_analysis/Sensitivity_analysis.html) | `vignette_extracted.R` |
| `07_ampute/` | [Generate missing values with ampute](https://rianneschouten.github.io/mice_ampute/vignette/ampute.html) | `vignette_extracted.R` |
| `08_futuremice/` | [futuremice parallel wrapper](https://www.gerkovink.com/micereference/futuremice/Vignette_futuremice.html) | `vignette_extracted.R` |

Each subdirectory also contains `vignette.html`, `golden_outputs.json`, and `vignette_blocks.json` where applicable.

## How PyMICE uses these files

1. **`golden_outputs.json`** — frozen R console snapshots compared in `devtools/runners/v0N_*.py` walkthroughs.
2. **`vignette_extracted.R`** — reference execution order for chain helpers in `devtools/lib/vignette_rng.py`.
3. **`tests/vignettes/`** — subprocess R checks and draw-order parity tests.
4. **`devtools/run_vignettes.py`** — generates HTML reports with parity badges.

Current status (0.1.0): all eight vignettes pass structural alignment (0 errors / 0 warnings); RNG chain steps 27/27 match. See [`docs/dev/PARITY_STATUS.md`](../docs/dev/PARITY_STATUS.md).

## Regenerating extracted R

```bash
python3 reference/extract_vignette_code.py
```

## Refreshing goldens

```bash
python devtools/refresh_goldens.py --vignette draw_order,05,06,07
```

## License note

Vignette HTML and extracted R code are **third-party tutorial material** (van Buuren, Vink, Schouten, and the `mice` authors). They are stored here for reproducibility testing only and are **not** redistributed as part of the Python wheel. See [`docs/dev/ATTRIBUTION.md`](../docs/dev/ATTRIBUTION.md).