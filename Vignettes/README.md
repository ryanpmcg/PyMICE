# Vignettes — R reference scripts for verification

This folder holds **reference material** from published `mice` tutorials. It is not part of the installable Python package; it exists to drive parity testing against R `mice`.

## Layout

| Folder | Source | Extracted R |
|--------|--------|-------------|
| `01_ad_hoc_and_mice/` | [Ad hoc methods and mice](https://www.gerkovink.com/miceVignettes/Ad_hoc_and_mice/Ad_hoc_methods.html) | `vignette_extracted.R` |
| `02_convergence_and_pooling/` | [Convergence and pooling](https://www.gerkovink.com/miceVignettes/Convergence_pooling/Convergence_and_pooling.html) | `vignette_extracted.R` |
| `03_missingness_inspection/` | [Missingness inspection](https://www.gerkovink.com/miceVignettes/Missingness_inspection/Missingness_inspection.html) | `vignette_extracted.R` |
| `04_passive_post_processing/` | [Passive imputation and post-processing](https://www.gerkovink.com/miceVignettes/Passive_Post_processing/Passive_imputation_post_processing.html) | `vignette_extracted.R` |
| `05_multilevel_data/` | [Imputing multilevel data](https://www.gerkovink.com/miceVignettes/Multi_level/Multi_level_data.html) | `vignette_extracted.R` |
| `06_sensitivity_analysis/` | [Sensitivity analysis](https://www.gerkovink.com/miceVignettes/Sensitivity_analysis/Sensitivity_analysis.html) | `vignette_extracted.R` |
| `07_ampute/` | [Generate missing values with ampute](https://rianneschouten.github.io/mice_ampute/vignette/ampute.html) | `vignette_extracted.R` |
| `08_futuremice/` | [futuremice parallel wrapper](https://www.gerkovink.com/miceVignettes/futuremice/Vignette_futuremice.html) | `vignette_extracted.R` |

Each subdirectory also contains `vignette.html` (downloaded snapshot).

## How to use

1. Install R `mice` (≥ 3.19): `install.packages("mice")`
2. Run extracted scripts in R and capture golden outputs (`.rds`, CSV, tolerance tables).
3. Mirror the same workflows in `tests/vignettes/` once `pymice` API exists.
4. Compare imputations with seeded runs (fixed `seed`, `m`, `maxit`).

## Regenerating extracted R

```bash
python3 scripts/extract_vignette_code.py
```

## License note

Vignette HTML and extracted R code are **third-party tutorial material** (van Buuren, Vink, Schouten, and the `mice` authors). They are stored here for reproducibility testing only and are **not** redistributed as part of the Python wheel. See `ATTRIBUTION.md`.