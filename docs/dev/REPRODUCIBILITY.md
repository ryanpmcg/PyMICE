# Reproducibility and cross-language parity

Notes for PyMICE development, validation, and publication.

## Random number generation (R vs Python)

### Summary

By default, PyMICE uses NumPy's PCG64 generator (`rng="numpy"`). Stochastic imputations therefore differ from R `mice` even when the same numeric `seed` is supplied.

For vignette replication and cross-checks against R, pass **`rng="r"`** to use R's default Mersenne-Twister stream (via a bundled `Rscript` server). With `rng="r"`, `pmm`, `norm`, and `norm.nob` on the bundled `nhanes` dataset match R reference outputs bit-for-bit under `seed=123`.

### Choosing an RNG backend

```python
from pymice import mice, RngBackend

# Default: NumPy PCG64 (fast, independent of R)
imp = mice(data, seed=123)

# Explicit backends
imp = mice(data, seed=123, rng="numpy")    # same as default
imp = mice(data, seed=123, rng="legacy")   # NumPy MT19937 (not R-identical)
imp = mice(data, seed=123, rng="r")        # R default MT (requires Rscript)

# Or pass your own numpy Generator
imp = mice(data, rng=np.random.default_rng(42))
```

| `rng` value | Engine | R parity | Notes |
|-------------|--------|----------|-------|
| `"numpy"` (default) | NumPy PCG64 | No | Recommended for new Python workflows |
| `"legacy"` | NumPy MT19937 | No | Alternative NumPy stream; `seed` required |
| `"r"` | R `stats` RNG | Yes for PMM/norm paths | Requires R; slower (subprocess) |
| `numpy.random.Generator` | User-supplied | Depends | Full control for custom workflows |

Set `PYMICE_R_PAN=0` to disable the optional R `pan` backend for `2l.pan` independently of `rng`.

### Optional R / sklearn backends (independent of `rng`)

These backends call R or scikit-learn for specific imputation methods. They auto-activate when dependencies are available unless disabled.

| Variable | Methods | Requires |
|----------|---------|----------|
| `PYMICE_R_PAN` | `2l.pan` | R + `pan` |
| `PYMICE_R_LMER` | `2l.lmer`, `2l.bin` | R + `mice` + `lme4` + `MASS` |
| `PYMICE_R_AMPUTE` | `ampute()` chain | R + `mice` + `jsonlite` |
| `PYMICE_SKLEARN` | `lasso.*`, `lda` | `pip install pymice[ml]` |

Set any variable to `0` to force the NumPy/Python fallback.

### R prerequisites (`rng="r"` only)

When `rng="r"` is requested, PyMICE checks for `Rscript` and CRAN packages `mice` and `pan`.
The check does **not** run for the default `rng="numpy"` backend.

```python
from pymice import ensure_r_prerequisites, check_r_prerequisites

status = check_r_prerequisites()          # inspect only
ensure_r_prerequisites(install=True)      # run bundled installer if needed
```

Environment variables:

| Variable | Effect |
|----------|--------|
| `PYMICE_AUTO_INSTALL_R=1` | Auto-install R/packages when `rng="r"` in library code |
| `PYMICE_SKIP_R_INSTALL=1` | Disable auto-install in vignettes and `ensure_r_prerequisites(install=True)` |

Vignette runners (`devtools/run_vignettes.py`) call the installer by default before executing demos.

The chosen backend is stored on the returned `mids` object as `rng_backend` and reused by `continue_imputation()`.

### Why imputations differ by default

| Factor | R `mice` | PyMICE (`rng="numpy"`) |
|--------|----------|------------------------|
| RNG engine | Mersenne Twister (default) | NumPy PCG64 |
| Draw ordering | Fixed by R `sampler()` call sequence | Matched structurally, not byte-for-byte |
| PMM donors | `matchindex` C++ with R `.Random.seed` | Python port of `matchindex`; independent RNG stream |

Even one divergent draw during initialization or an early FCS iteration changes all subsequent imputations.

### What does match

- **Deterministic methods** (e.g. `mean`): `nhanes` golden tests match R within machine precision (`atol ≤ 1e-12`) with any backend.
- **Stochastic methods with `rng="r"`**: `pmm`, `norm`, `norm.nob` on `nhanes` match R goldens (`tests/goldens/r/`).
- **Observed cells**: Never altered; always identical to input.
- **Pooling (Rubin 1987 + Barnard–Rubin df)**: Independent of imputation RNG when given the same per-imputation **estimates and standard errors**; `pool.scalar` matches R reference formulas exactly.

### Statistical interpretation

MICE treats imputation as a proper stochastic step (Rubin, 1987). Valid inference depends on:

1. Correct FCS / univariate imputation models
2. Correct Rubin pooling of **estimates**, not of raw multiply imputed rows
3. Adequate number of imputations `m`

Re-running R `mice` with a different seed also yields different imputations but valid pooled inference. PyMICE with `rng="numpy"` is in the same class: **algorithmically equivalent, RNG-independent**.

### Validation strategy used in this project

1. **Structural parity**: FCS loop, predictor matrix, visit sequence, method dispatch aligned with JSS (2011) and R `mice` 3.19 behavior.
2. **Deterministic goldens**: `mean` imputation vs R on `nhanes`.
3. **R-RNG goldens**: `pmm` / `norm` / `norm.nob` vs R when `rng="r"`.
4. **Session chain helpers**: `devtools/lib/vignette_rng.py` mirrors R tutorial draw order for V01–V06; goldens refreshed via `regenerate_draw_order_goldens.py`, `regenerate_v05_goldens.py`, `regenerate_v06_goldens.py`.
5. **Stochastic checks**: Observed data preserved; imputations finite and in plausible ranges; PMM donors drawn from observed values.
6. **Pooling goldens**: `pool.scalar` and `lm(bmi ~ hyp + chl)` workflow with `method="mean"` (stable imputations) vs R.
7. **Multilevel tolerance**: `2l.norm` / `2l.pan` moment checks within ~0.15 on V05 steps 21–26 (documented partial).

### Reporting recommendations (publication)

When describing PyMICE results alongside or in comparison to R `mice`:

- Report `pymice` version, `m`, `maxit`, methods, `rng` backend, and pooling rule (Rubin 1987 / Barnard–Rubin 1999).
- State that default PyMICE uses NumPy PCG64; use `rng="r"` only when R-matching imputations are required.
- Where comparison to R is shown, prefer **pooled estimates, SEs, and FMI** over cell-level imputation tables unless `mean`, fixed `data_init`, or `rng="r"` is used.
- Cite van Buuren & Groothuis-Oudshoorn (2011) for MICE methodology and Rubin (1987) / Barnard & Rubin (1999) for pooling.
- Full release checklist and BibTeX: [`PUBLICATION.md`](PUBLICATION.md).

## References

- Barnard, J., & Rubin, D. B. (1999). Small sample degrees of freedom with multiple imputation. *Biometrika*, 86(4), 948–955.
- Rubin, D. B. (1987). *Multiple Imputation for Nonresponse in Surveys*. Wiley.
- van Buuren, S., & Groothuis-Oudshoorn, K. (2011). mice: Multivariate Imputation by Chained Equations in R. *Journal of Statistical Software*, 45(3), 1–67.