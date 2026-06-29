# Reproducibility and cross-language parity

Notes for PyMICE development, validation, and publication.

## Random number generation (R vs Python)

### Summary

PyMICE does **not** reproduce R `mice` imputations bit-for-bit when the same numeric `seed` is supplied. This is **expected** and does **not** indicate incorrect implementation. Inference from multiply imputed data (pooled estimates, standard errors, fractions of missing information) should agree with R within Monte Carlo variation when the same models and pooling rules are used.

### Why imputations differ

| Factor | R `mice` | PyMICE |
|--------|----------|--------|
| RNG engine | Mersenne Twister (default) | NumPy `PCG64` via `numpy.random.Generator` |
| Draw ordering | Fixed by R `sampler()` call sequence | Matched structurally, not byte-for-byte |
| PMM donors | `matchindex` C++ with R `.Random.seed` | Python port of `matchindex`; independent RNG stream |

Even one divergent draw during initialization or an early FCS iteration changes all subsequent imputations. Stochastic methods (`pmm`, `norm`, `norm.nob`, `logreg`, `polyreg`) therefore produce different filled datasets than R for equal seeds.

### What does match

- **Deterministic methods** (e.g. `mean`): `nhanes` golden tests match R within machine precision (`atol ≤ 1e-12`).
- **Observed cells**: Never altered; always identical to input.
- **Pooling (Rubin 1987 + Barnard–Rubin df)**: Independent of imputation RNG when given the same per-imputation **estimates and standard errors**; `pool.scalar` matches R reference formulas exactly.

### Statistical interpretation

MICE treats imputation as a proper stochastic step (Rubin, 1987). Valid inference depends on:

1. Correct FCS / univariate imputation models
2. Correct Rubin pooling of **estimates**, not of raw multiply imputed rows
3. Adequate number of imputations `m`

Re-running R `mice` with a different seed also yields different imputations but valid pooled inference. PyMICE is in the same class: **algorithmically equivalent, RNG-independent**.

### Validation strategy used in this project

1. **Structural parity**: FCS loop, predictor matrix, visit sequence, method dispatch aligned with JSS (2011) and R `mice` 3.19 behavior.
2. **Deterministic goldens**: `mean` imputation vs R on `nhanes`.
3. **Stochastic checks**: Observed data preserved; imputations finite and in plausible ranges; PMM donors drawn from observed values.
4. **Pooling goldens**: `pool.scalar` and `lm(bmi ~ hyp + chl)` workflow with `method="mean"` (stable imputations) vs R.

### Reporting recommendations (publication)

When describing PyMICE results alongside or in comparison to R `mice`:

- Report `m`, `maxit`, methods, and pooling rule (Rubin 1987 / Barnard–Rubin 1999).
- State that PyMICE uses NumPy RNG; **do not** claim byte-identical imputations with R for stochastic methods.
- Where comparison to R is shown, prefer **pooled estimates, SEs, and FMI** over cell-level imputation tables unless `mean` or fixed `data_init` is used.
- Cite van Buuren & Groothuis-Oudshoorn (2011) for MICE methodology and Rubin (1987) / Barnard & Rubin (1999) for pooling.

### Optional future work (not required for validity)

An optional `r_compat` mode could synchronize with R `.Random.seed` via `rpy2` for debugging and strict vignette replication. This is not planned for v1.0 and is not required for statistically valid MI.

## References

- Barnard, J., & Rubin, D. B. (1999). Small sample degrees of freedom with multiple imputation. *Biometrika*, 86(4), 948–955.
- Rubin, D. B. (1987). *Multiple Imputation for Nonresponse in Surveys*. Wiley.
- van Buuren, S., & Groothuis-Oudshoorn, K. (2011). mice: Multivariate Imputation by Chained Equations in R. *Journal of Statistical Software*, 45(3), 1–67.