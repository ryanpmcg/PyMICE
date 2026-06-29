# Reference — R `mice` source snapshots

Read-only copies of key functions from [amices/mice](https://github.com/amices/mice) (CRAN 3.19.0, GPL-2|GPL-3).

These files inform the Python reimplementation. **Do not paste GPL R code into `src/pymice/`** — use them to understand behavior, edge cases, and API contracts.

| File | Role |
|------|------|
| `mice.R` | Main MICE / FCS driver |
| `mice.impute.pmm.R` | Predictive mean matching |
| `mice.impute.norm.R` | Bayesian linear regression (normal) |
| `mice.impute.logreg.R` | Binary logistic imputation |
| `mice.impute.polyreg.R` | Unordered categorical (polytomous) |
| `pool.R` | Rubin's rules pooling |
| `complete.R` | Completed-data extraction |
| `md.pattern.R` | Missingness pattern |
| `make.predictorMatrix.R` | Default predictor matrix |
| `make.method.R` | Default method vector |

Refresh from upstream:

```bash
bash scripts/fetch_reference_r.sh
```