# PyMICE ↔ R `mice` Parity Status

Last updated: 2026-07-05

This document records **what has been implemented** to align PyMICE with the R [`mice`](https://cran.r-project.org/package=mice) reference tutorials (V01–V08), the **current verification status**, and **remaining gaps**. For the active work queue see [`PARITY_IMPLEMENTATION_PLAN.md`](PARITY_IMPLEMENTATION_PLAN.md). For RNG semantics see [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

---

## Executive summary

| Area | Status |
|------|--------|
| **Report structure (Tier A)** | All eight vignettes pass `audit_vignette` (0 errors, 0 warnings) |
| **Deterministic console (Tier B)** | Observed-data tables, setup matrices, pooling formulas, Cox on chain-aligned mids |
| **Algorithmic fidelity (Tier C)** | Core FCS loop, 35 methods, passive/post/parallel/ampute/Cox stacks |
| **Bit-for-bit RNG (Tier D)** | Optional via `rng="r"`; session chains aligned for V01–V06 |

PyMICE **0.1.0 is publication-ready** for algorithmic equivalence under independent RNG. Vignette reports label stochastic steps **PARTIAL** when imputed values differ from frozen R snapshots — expected unless `rng="r"` and chain order match.

**Latest closure (2026-07-05):** Full R `methods(mice)` surface (35 methods); optional `lme4`/`sklearn` backends; `maintain_parity.py` maintenance wrapper; V08 `futuremice(print=False)` fix; all eight vignette walkthroughs pass `run_all.sh`. See [`PUBLICATION.md`](PUBLICATION.md) for release checklist.

---

## Parity tiers

| Tier | Meaning | Goal |
|------|---------|------|
| **A — Report structure** | Steps, prose, figures, golden mapping | ✅ All V01–V08 |
| **B — Deterministic console** | Tables, counts, matrices on observed data | ✅ Most steps; cosmetic layout diffs documented |
| **C — Algorithmic** | Correct imputation method math | ✅ Core paths; see unimplemented methods below |
| **D — Bit-for-bit RNG** | Identical imputations under fixed seed | Optional; `rng="r"` + chain helpers (V01–V06) |

---

## Cross-cutting infrastructure delivered

### Engine and API

- Full FCS / Gibbs sampler aligned with JSS (2011) and R `mice` 3.19 visit-sequence semantics
- `mice()`, `mice_mids()`, `continue_imputation()` (`mice.mids` warm start)
- `complete()`, `with_mids()`, `pool()`, `summary_pool()`, `anova()`
- `quickpred()`, `md.pattern()`, `flux()`, diagnostic plots (matplotlib)
- R-style kwargs via `r_compat.normalize_mice_kwargs()` (`maxit`, `printFlag`, `n.core`, …)

### Imputation methods (implemented)

All 35 registered methods (full R `methods(mice)` snapshot): `pmm`, `norm`, `norm.nob`, `norm.boot`, `norm.predict`, `mean`, `sample`, `midastouch`, `logreg`, `logreg.boot`, `polyreg`, `polr`, `cart`, `rf`, `lda`, `quadratic`, `micemean`, `mnar`, `ri`, `2l.norm`, `2l.pan`, `2l.lmer`, `2l.bin`, `2lonly.mean`, `2lonly.norm`, `2lonly.pmm`, `jomoImpute`, `panImpute`, `jomo2con`, `jomo2ran`, `lasso.norm`, `lasso.logreg`, `lasso.select.norm`, `lasso.select.logreg`, `2logreg`, plus passive `~ I(...)`, `post` hooks, `squeeze` / `post_squeeze`

### RNG backends (`rng` argument)

| Value | Engine | R bit-parity |
|-------|--------|--------------|
| `"numpy"` (default) | PCG64 | No |
| `"legacy"` | NumPy MT19937 | No |
| `"r"` | R `stats` MT via `Rscript` | Yes for PMM/norm on isolated calls |

`continue_imputation()` preserves `rng_backend` from source `mids`.

### Optional R backends

| Feature | Env / flag | Purpose |
|---------|------------|---------|
| `2l.pan` | `PYMICE_R_PAN` (auto) | R `pan::pan` Fortran sampler |
| `2l.lmer` / `2l.bin` | `PYMICE_R_LMER` (auto) | R `mice` + `lme4::lmer` / `glmer` |
| `lasso.*` / `lda` | `PYMICE_SKLEARN` (auto) | scikit-learn when `[ml]` extra installed |
| `ampute` | `PYMICE_R_AMPUTE` (auto) | Bit-identical MCAR/MAR patterns |
| Prerequisites | `ensure_r_prerequisites()` | Auto-install R + CRAN deps for vignettes |

### Parallel imputation (V08)

- `futuremice()`, `parallel_mice()`, `mice(..., n_jobs=N)`
- `distribute_imputations()` — R `cut(1:m, n.core)` via pandas
- `ProcessPoolExecutor` workers; `SeedSequence.spawn()` per worker
- `ibind()` merge; `Mids.parallelseed` / `parallel_n_core` metadata

### Survival / sensitivity (V06)

- `leiden_coxph()` — Leiden `cda` workflow with lifelines strata
- Cox formatters in `devtools/lib/r_style.py`
- δ-adjustment via `post_add` on pooled mids chains
- `regenerate_v06_goldens.py` — Cox/pool/HR/qbar golden refresh

### Ampute (V07)

- Native Python `ampute()` with patterns/weights/MNAR odds
- `run_ampute_chain()` — shared RNG stream + R-style `mvrnorm` warmup (V07 native path)
- Optional R `mice::ampute` one-shot chain (`r_ampute_backend.py`)

### Vignette chain helpers (`devtools/lib/vignette_rng.py`)

Session-ordered `mice()` sequences mirroring R tutorial draw order:

- `run_v01_mice_chain()` — nhanes mean → densityplot RNG advance → norm.predict → norm.nob → PMM
- `run_v02_mice_chain()` — nhanes + nhanes2 convergence/pooling
- `run_v03_boys_chain()`, `run_v03_mammalsleep_chain()`
- `run_v04_chain()` — mammalsleep passive → boys norm/post → PMM → passive BMI
- `run_v05_multilevel_chain()` — popNCR multilevel session
- `run_v06_leiden_delta_chain()` / `run_v06_mammalsleep_delta_chain()` — δ-adjustment loops

### Verification tooling

- `devtools/audit_vignette_alignment.py` — structural manifest audit
- `devtools/audit_rng_parity.py` — re-compare chain-aligned steps vs goldens
- `devtools/maintain_parity.py` — run structural + RNG audits; refresh `parity_backlog.json`
- `devtools/regenerate_draw_order_goldens.py` — refresh V02–V04 golden outputs
- `devtools/regenerate_v05_goldens.py` — refresh V05 step 16 golden
- `devtools/regenerate_v06_goldens.py` — refresh V06 Cox/pool/qbar golden outputs
- `devtools/parity_backlog.json` — tracked draw-order items (`audit_rng_parity.py`: 27/27 match as of 2026-07-05)
- `tests/vignettes/test_*_draw_order_parity.py` — subprocess R checks

---

## Vignette status (V01–V08)

### V01 — Ad hoc MICE

| Delivered | Notes |
|-----------|-------|
| Deterministic steps 2–7, 13–14 | Goldens match |
| `run_v01_mice_chain()` | Session stream; `advance_vignette_r_rng()` mirrors lattice |
| `format_mids_print_r()` | Filters `visitSequence` to imputed vars only (excludes `age`) |
| Steps 8–9, 11–12 | `norm.predict` / PMM RNG partial under default `rng` (exact with `rng="r"`) |

### V02 — Convergence and pooling

| Delivered | Notes |
|-----------|-------|
| Predictor matrices, `maxit=0`, methods listing | Exact |
| `continue_imputation(imp3, maxit=35)` | Step 5 extended trace |
| Steps 7–8 mira/pool | Goldens refreshed 2026-07-05; `exact=True` on main blocks |
| Plots | matplotlib partial |

### V03 — Missingness inspection

| Delivered | Notes |
|-----------|-------|
| Boys observed summaries, md.pattern, logical vectors | Exact |
| `imp1` PMM chain + pool | Goldens refreshed 2026-07-05 |
| Mammalsleep pool steps 12–14 | Goldens refreshed |
| Plots, factor labels | Partial |

### V04 — Passive imputation

| Delivered | Notes |
|-----------|-------|
| Passive `ts = sws + ps` | Numeric constraint check |
| `post_squeeze` on `tv` | Frequency tables exact (goldens refreshed) |
| Passive BMI `~ I(wgt/(hgt/100)^2)` | Visit order imputes `hgt`/`wgt` before passive `bmi`; constraint exact |
| Triple-passive `sqrt(wgt/bmi)` | Runs with `seed=123`; iteration log format differs |
| Circular BMI fix (step 9) | `pred[hgt,wgt,bmi] <- 0` wired |

### V05 — Multilevel data

| Delivered | Notes |
|-----------|-------|
| `2l.norm`, `2l.pan` (R backend), `2lonly.mean` | Moment tests within ~0.15 |
| ICC tables on observed + `orig` | Exact |
| 30 figures mapped | Alignment audit clean |
| Step 9.24 imputed summary | atol=0.2 partial |
| Step 16 `head(complete(imp2))` | Exact (golden refreshed 2026-07-05) |
| Step 26 logged-events warning | Exact on session chain |
| Steps 21–26 | Setup matrices exact; imputed densities within ~0.15 moment tolerance |

### V06 — Sensitivity analysis

| Delivered | Notes |
|-----------|-------|
| `flux()`, md.pattern, δ vector | Exact |
| `leiden_coxph()` + `pool()` steps 11–13 | Exact (goldens refreshed 2026-07-05) |
| `run_v06_mammalsleep_delta_chain()` step 13 | δ qbar table exact |
| Kaplan–Meier, fluxplot, δ diagnostic plots | matplotlib partial |

### V07 — Ampute

| Delivered | Notes |
|-----------|-------|
| R backend steps 4, 9, 10.8, 11 | Exact when `PYMICE_R_AMPUTE` active |
| Native ampute | Steps 3.3, 5.5, 10.7 partial vs older R goldens |
| Deep reference (`patterns`, `odds`, `run`) | Reference-only step 12 in walkthrough |

### V08 — futuremice

| Delivered | Notes |
|-----------|-------|
| `futuremice()`, `parallel_mice()`, `mice(n_jobs)` | Process pool + `ibind` |
| Steps 3–4, `parallelseed` reproducibility | Exact / self-consistent |
| `print=False` default | Fixed 2026-07-05 (no builtin shadowing) |
| Steps 5–7 pooled tables | Partial (no R snapshot blocks; RNG) |
| Wall-clock benchmarks | Skipped (R-only; explicit skip in step 8) |

---

## R surface coverage (`r_gaps.py`)

All R imputation methods listed in the V02 `methods(mice)` snapshot are now registered in PyMICE (2026-07-05), including multilevel (`2l.bin`, `2l.lmer`, `2lonly.norm`, `2lonly.pmm`), sensitivity (`mnar`, `ri`), `quadratic`, `lasso.*`, `lda`, `logreg.boot`, `micemean`, and level-2 JOMO aliases (`jomo2con`, `jomo2ran`).

**Utilities:** `as_mids()`, `cbind_mids()`, `rbind_mids()` implemented in `mids_construct.py`. Horizontal imputation merge remains `ibind()`.

---

## Remaining gaps (priority order)

### P1 — Optional RNG / algorithm

| Item | Vignette | Notes |
|------|----------|-------|
| Default `rng="numpy"` imputations | V01 steps 8–9, 11–12 | Chain-aligned with `rng="r"`; not a functional gap |
| `parallelseed` when unset | V08 steps 5–7 | Reproducible when `parallelseed` set explicitly |
| Native ampute drift | V07 steps 3.3, 5.5, 10.7 | vs older R 4.5.2 goldens; R backend exact |
| `norm.predict` OLS tolerance | V01 steps 8–9 | Optional R `lm` backend |
| Multilevel sampler moments | V05 steps 9.24, 21–26 | Documented ~0.15 / atol=0.2; not bit-identical |

### P2 — Cosmetic / rendering

- matplotlib vs lattice diagnostic plots (all vignettes)
- Factor labels vs numeric codes in `summary()` / `str()` (V01, V03, V05)
- Float formatting, R row names on `tail()`, help pager layout
- V06 Kaplan–Meier / fluxplot rendering
- V04 step 9 iteration event log format vs R

### P3 — Optional fidelity

- [x] `2l.lmer` / `2l.bin` — optional R `lme4` backend (`PYMICE_R_LMER`; NumPy GLS fallback)
- [x] `lasso.*` / `lda` — auto-detect scikit-learn (`PYMICE_SKLEARN`; OLS/logreg fallback)
- [x] V08 wall-clock benchmark figures — explicit skip in step 8 (R-only)
- [x] V07 deep reference (`patterns`, `odds`, `run`) — reference-only step 12 documented

### P4 — Maintenance

- [x] `devtools/maintain_parity.py` — structural + RNG audit wrapper
- [x] `parity_backlog.json` — 11 tracked items; refresh via `maintain_parity.py`

---

## Verification commands

```bash
cd PyMICE
source ~/.venvs/brain-pymice/bin/activate

# Structural alignment (all vignettes)
python devtools/audit_vignette_alignment.py

# RNG re-compare + backlog refresh (preferred)
python devtools/maintain_parity.py

# Or individually:
python devtools/audit_rng_parity.py

# Refresh draw-order / chain goldens
python devtools/regenerate_draw_order_goldens.py   # V02–V04
python devtools/regenerate_v05_goldens.py          # V05 step 16
python devtools/regenerate_v06_goldens.py          # V06 Cox/pool/qbar

# Tests
pytest tests/vignettes/ tests/unit/test_parallel_fidelity.py tests/unit/test_passive.py -q
pytest tests/unit/test_vignette_blocks.py tests/unit/test_ampute_chain.py -q
```

---

## Key file index

| Path | Role |
|------|------|
| `docs/dev/PARITY_STATUS.md` | This document — accomplishments + status |
| `docs/dev/PUBLICATION.md` | PyPI release checklist and citation |
| `docs/dev/PARITY_IMPLEMENTATION_PLAN.md` | Post-release maintenance queue |
| `docs/dev/REPRODUCIBILITY.md` | RNG backends and publication guidance |
| `CHANGELOG.md` | Version history |
| `devtools/lib/parity_docs.py` | Per-vignette report blurbs |
| `devtools/lib/vignette_rng.py` | Session chain helpers |
| `devtools/parity_backlog.json` | Draw-order backlog tracker |
| `reference/*/golden_outputs.json` | Frozen R console outputs |
| `src/pymice/r_gaps.py` | Unimplemented method registry |

---

## References

- van Buuren & Groothuis-Oudshoorn (2011). *mice: Multivariate Imputation by Chained Equations in R.* JSS 45(3).
- R vignettes: `PyMICE/reference/*/vignette_extracted.R`