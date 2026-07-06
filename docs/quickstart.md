# Quick start

```python
import pymice
from pymice import mice, complete, with_mids, pool, summary_pool

data, names = pymice.load_nhanes()
imp = mice(data, column_names=names, seed=123)

fit = with_mids(imp, formula="bmi ~ age + hyp + chl")
print(summary_pool(pool(fit)))
```

## R-aligned imputations

Requires `Rscript` and CRAN package `mice`:

```python
imp_r = mice(data, column_names=names, seed=123, rng="r")
```

## Parallel chains

```python
from pymice import futuremice

imp_par = futuremice(
    data, column_names=names, m=5, parallelseed=123, n_core=2, print=False
)
```

See [dev/REPRODUCIBILITY.md](dev/REPRODUCIBILITY.md) for RNG backends and publication reporting.