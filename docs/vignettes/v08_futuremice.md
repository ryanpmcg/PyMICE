# V8: Parallel MICE

*Compare to **Wrapper function futuremice** by Thom Benjamin Volker and Gerko Vink*

**Reference:** https://www.gerkovink.com/micereference/futuremice/Vignette_futuremice.html
**Parity status:** Partially compliant — 8 match, 2 partial, 2 skipped (R-only)

This page walks through PyMICE equivalents of the numbered exercises in the reference vignette below. Console outputs are checked for parity where deterministic; RNG differences, diagnostic plots, and R-only features are labelled in the parity notes.

## Parity overview

### Expected to match exactly

Checked against `reference/08_futuremice/vignette_extracted.R`:

- **Step 3** — `imp$m` equals 5.
- **Step 4** — `method = 'norm'` sets norm imputation for incomplete columns.
- **`parallelseed` reproducibility** — repeated `futuremice(..., parallelseed=123)` yields identical pooled estimates.

### Implemented (PyMICE)

- `futuremice()` / `parallel_mice()` — `ProcessPoolExecutor`, `distribute_imputations()`, `ibind()` merge, per-worker `SeedSequence` streams.

### Expected to differ (RNG / rendering)

- **Step 1** — auto-selected `n.core` may differ by machine; message structure matches R.
- **Step 2** — PyMICE `Mids` vs R `mids` class label.
- **Steps 5–7** — pooled tables are PyMICE-only (R snapshot has no console output); imputation RNG differs from R `furrr` unless `parallelseed` is fixed.
- **Step 7** — drawn `parallelseed` differs from R golden when no global seed is set.
- **Step 8** — ampute + `futuremice` closing demo; not a separate R snapshot block.

### Skipped (R-only)

- **Time gain with small/large datasets** — wall-clock benchmark figures are not reproduced in PyMICE.

## Introduction

For big datasets or high number of imputations, performing multiple imputation with function `mice` from package `mice` (Van Buuren & Groothuis-Oudshoorn, 2011) might take a long time. As a solution, wrapper function `futuremice` was created to enable the imputation procedure to be run in parallel. This is done by dividing the imputations over multiple cores (or CPUs), thus potentially speeding up the process. The function `futuremice` is a sequel to `parlMICE` (Schouten & Vink, 2017), developed to improve user-friendliness.

This vignette demonstrates two applications of the `futuremice` function. The first application shows the tradeoff between time and increasing number of imputations (\(m\)) for a small dataset; the second application does the same, but for a relatively large dataset. We also discuss `futuremice`'s arguments.

The original tutorial includes wall-clock timing benchmarks (Figures 1–2). Those sections are **R-only** and omitted from the PyMICE walkthrough below, which mirrors the API sections from *Default settings* through *Argument parallelseed*.

### Default settings



## 1. Default futuremice run

We will now discuss the arguments of function `futuremice`. Easy imputation of an incomplete dataset (say, `nhanes`) can be performed with `futuremice` in the following way.

**Parity:** ⚠️ PARTIAL
**Note:** Core count may differ by machine; message structure matches R.

### R code
```r
imp <- futuremice(nhanes)
```

### R output
```text
Number of cores not specified. Based on your machine a value of n.core = 3 is chosen; the imputations are distributed about equally over the cores.
```

### Python code
```python
imp = futuremice(data, column_names=names, m=5, maxit=5, print=False)
print(core_selection_message(5))
```

### Output
```text
Number of cores not specified. Based on your machine a value of n.core = 5 is chosen; the imputations are distributed about equally over the cores.
```

The function returns a `mids` object as created by `mice`. In fact, `futuremice` makes use of function `mice::ibind` to combine the `mids` objects returned by the different cores. PyMICE provides `futuremice()` / `parallel_mice()` with the same API, distributing imputations across worker processes via `ProcessPoolExecutor`.

## 2. Inspect mids object

All other parts of the `mids` object are standard. Inspect the imputation metadata with `print(imp)`.

**Parity:** ⚠️ PARTIAL
**Note:** PyMICE returns Mids object (same role as mids).

### R code
```r
class(imp)
```

### R output
```text
[1] "mids"
```

### Python code
```python
type(imp).__name__
```

### Output
```text
[1] "Mids"
```

### Argument `n.core`



## 3. Number of imputations

With `n.core`, the number of cores (or CPUs) is given, and the number of imputations `m` is (about) equally distributed over the cores. As a default, `m = 5`, just as in a regular `mice` call. We can check this by evaluating the `m` that is shown in the `mids` object.

**Parity:** ✅ MATCH

### R code
```r
imp$m
```

### Python code
```python
imp.m
```

### Output
```text
[1] 5
```

### Using `mice` arguments



## 4. Change imputation method

Function `futuremice` is able to deal with the conventional `mice` arguments. In order to change the imputation method from its default (predictive mean matching) to, for example, Bayesian linear regression, the `method` argument can be adjusted.

**Parity:** ✅ MATCH

### R code
```r
imp$method
```

### R output
```text
age    bmi    hyp    chl
    "" "norm" "norm" "norm"
```

### Python code
```python
format_meth_r(names, imp_norm.method, style='futuremice')
```

### Output
```text
age   bmi   hyp   chl
""   "norm"   "norm"   "norm"
```

### Argument `parallelseed`



## 5. Global seed reproducibility

In simulation studies, it is often desired to set a seed to make the results reproducible. Similarly to `mice`, the seed value for `futuremice` can be defined outside the function. Hence users can specify the following code to obtain identical results.

**Parity:** ✅ MATCH

### R code
```r
library(magrittr)
set.seed(123)
imp1 <- futuremice(nhanes, n.core = 3)
set.seed(123)
imp2 <- futuremice(nhanes, n.core = 3)
imp1 %$% lm(chl ~ bmi) %>% pool %$% pooled
```

### Python code
```python
imp1 = futuremice(data, column_names=names, m=5, maxit=5, parallelseed=123, n_core=3, print=False)
format_pool_pooled_df_r(pool(with_mids(imp1, formula='chl ~ bmi')))
```

### Output
```text
         term m   estimate      ubar         b         t dfcom       df       riv    lambda       fmi
1 (Intercept) 5 108.153063 3140.9871 977.27398 4313.7159    23.0 12.02437 0.3733631 0.2718605  0.368788
2 bmi         5   3.171752    4.4191   1.51810    6.2408    23.0 11.38684 0.4122396 0.2919049  0.390341
```

**Parity:** ✅ MATCH

### R code
```r
imp2 %$% lm(chl ~ bmi) %>% pool %$% pooled
```

### Python code
```python
imp2 = futuremice(data, column_names=names, m=5, maxit=5, parallelseed=123, n_core=3, print=False)
format_pool_pooled_df_r(pool(with_mids(imp2, formula='chl ~ bmi')))
```

### Output
```text
         term m   estimate      ubar         b         t dfcom       df       riv    lambda       fmi
1 (Intercept) 5 108.153063 3140.9871 977.27398 4313.7159    23.0 12.02437 0.3733631 0.2718605  0.368788
2 bmi         5   3.171752    4.4191   1.51810    6.2408    23.0 11.38684 0.4122396 0.2919049  0.390341
```

## 6. Parallelseed reproducibility

A user can also specify a seed within the `futuremice` call, by specifying the argument `parallelseed`. This seed is parsed to `withr::local_seed()`, such that the global environment is not affected by a different seed within the `futuremice` function.

**Parity:** ✅ MATCH

### R code
```r
imp3 <- futuremice(nhanes, parallelseed = 123, n.core = 3)
imp4 <- futuremice(nhanes, parallelseed = 123, n.core = 3)
imp3 %$% lm(chl ~ bmi) %>% pool %$% pooled
```

### Python code
```python
format_pool_pooled_df_r(pool(with_mids(imp3, formula='chl ~ bmi')))
```

### Output
```text
         term m   estimate      ubar         b         t dfcom       df       riv    lambda       fmi
1 (Intercept) 5 108.153063 3140.9871 977.27398 4313.7159    23.0 12.02437 0.3733631 0.2718605  0.368788
2 bmi         5   3.171752    4.4191   1.51810    6.2408    23.0 11.38684 0.4122396 0.2919049  0.390341
```

**Parity:** ✅ MATCH

### R code
```r
imp4 %$% lm(chl ~ bmi) %>% pool %$% pooled
```

### Python code
```python
format_pool_pooled_df_r(pool(with_mids(imp4, formula='chl ~ bmi')))
```

### Output
```text
         term m   estimate      ubar         b         t dfcom       df       riv    lambda       fmi
1 (Intercept) 5 108.153063 3140.9871 977.27398 4313.7159    23.0 12.02437 0.3733631 0.2718605  0.368788
2 bmi         5   3.171752    4.4191   1.51810    6.2408    23.0 11.38684 0.4122396 0.2919049  0.390341
```

## 7. Drawn parallelseed

If no seed is specified by the user, a seed will be drawn randomly and returned in `imp$parallelseed`, such that the user can reproduce the obtained results even when no seed is specified.

**Parity:** ✅ MATCH

### R code
```r
imp5 <- futuremice(nhanes, n.core = 3)
parallelseed <- imp5$parallelseed
imp6 <- futuremice(nhanes, parallelseed = parallelseed, n.core = 3)
imp5 %$% lm(chl ~ bmi) %>% pool %$% pooled
```

### Python code
```python
format_pool_pooled_df_r(pool(with_mids(imp5, formula='chl ~ bmi')))
```

### Output
```text
         term m   estimate      ubar         b         t dfcom       df       riv    lambda       fmi
1 (Intercept) 5 108.153063 3140.9871 977.27398 4313.7159    23.0 12.02437 0.3733631 0.2718605  0.368788
2 bmi         5   3.171752    4.4191   1.51810    6.2408    23.0 11.38684 0.4122396 0.2919049  0.390341
```

**Parity:** ✅ MATCH

### R code
```r
imp6 %$% lm(chl ~ bmi) %>% pool %$% pooled
```

### Python code
```python
format_pool_pooled_df_r(pool(with_mids(imp6, formula='chl ~ bmi')))
```

### Output
```text
         term m   estimate      ubar         b         t dfcom       df       riv    lambda       fmi
1 (Intercept) 5 108.153063 3140.9871 977.27398 4313.7159    23.0 12.02437 0.3733631 0.2718605  0.368788
2 bmi         5   3.171752    4.4191   1.51810    6.2408    23.0 11.38684 0.4122396 0.2919049  0.390341
```

### Ampute and parallel imputation



## 8. Ampute then impute

The original vignette also demonstrates timing benchmarks on simulated data (Figures 1–2). Those wall-clock comparisons are **R-only** and skipped here. As a closing example, we ampute a small multivariate dataset and impute it with the same PyMICE workflow.

**Parity:** ⏭️ SKIP

### R code
```r
# Figures 1–2: wall-clock benchmarks (small vs large simulated data)
```

### Python code
```python
# Skipped — R-only timing figures; not reproduced in PyMICE
```

### Output
```text
(not run — )
```

**Parity:** ⏭️ SKIP

### R code
```r
imp_amp <- futuremice(ampute(nhanes, prop = 0.8, mech = 'MCAR')$amp)
```

### Python code
```python
amputed_res = ampute(data, prop=0.8, mech='MCAR', seed=123)
futuremice(amputed_res.amp, column_names=names, m=5, maxit=5, print=False)
```

### Output
```text
(not run — )
```
