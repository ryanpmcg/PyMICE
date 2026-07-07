"""Shared disclaimer and per-vignette parity overview text."""

from __future__ import annotations

from lib.vignette_catalog import COMPARISON_DISCLAIMER

GLOBAL_DISCLAIMER = COMPARISON_DISCLAIMER

V01_PARITY_OVERVIEW = """\
### Expected to match exactly

These numbered steps are deterministic and are checked against `reference/01_ad_hoc_and_mice/vignette_extracted.R`:

- **Step 2** — `nhanes` row-level print
- **Step 3** — `summary(nhanes)` numeric summaries and NA counts
- **Step 4** — `md.pattern(nhanes)` pattern matrix (console table)
- **Step 5** — `lm(age ~ bmi)` on raw incomplete data (listwise deletion)
- **Step 6** — mean imputation iteration log (`method="mean"`, `m=1`, `maxit=1`)
- **Step 7** — `complete(imp)`, `colMeans(nhanes, na.rm=TRUE)`, pooled regression after mean imputation
- **Steps 11–12** — `norm.nob` `complete(imp)` and pooled `lm(age ~ bmi)` (session R RNG; draw order aligned with R vignette chain)
- **Step 13** — default `mice(nhanes)` iteration log, `print(imp)` mids summary (`visitSequence` excludes non-imputed `age`), `attributes(imp)`, `imp$data`, `imp$imp` PMM values (session stream; `run_v01_mice_chain()`)
- **Step 14** — `md.pattern(complete(imp, 3))`, `complete(imp, "long")`, `complete(imp, "broad")`

### Expected to differ (not bit-identical to R snapshot)

- **Step 1** — package load; no R console output to compare.
- **Step 2** — `help('nhanes')` static R pager snapshot (informational; text matches reference).
- **Step 4** — `md.pattern(nhanes)` grid layout and colours match R; rendering is matplotlib.
- **Step 7** — `densityplot(nhanes$bmi)` uses R ``bw.nrd0`` bandwidth and ``mdc`` palette; shape should closely match lattice.
- **Steps 8–9** — `norm.predict` after `densityplot(nhanes$bmi)` on session R stream (lattice RNG advance mirrored)."""

V02_PARITY_OVERVIEW = """\
### Expected to match exactly

These numbered steps are checked against `reference/02_convergence_and_pooling/vignette_extracted.R`:

- **Step 2** — default and modified `pred` matrices; `maxit=0` initializer matrix
- **Step 4** — `imp$meth` on `nhanes` and `nhanes2`; `summary(nhanes2)` factor layout; `methods(mice)` listing (static reference text)
- **Step 7** — `class(fit)` and `ls(fit)` names; `print(fit)` mira coefficients (`exact=True`); `summary(fit$analyses[[2]])` on imp3 (atol=0.15)
- **Step 8** — pooled `summary(pool.fit)` (`exact=True`; session R stream; goldens refreshed 2026-07-05)

### Expected to differ (RNG / rendering)

- **Step 1** — `mice(nhanes, m=3)` setup; no R console output to compare.
- **Step 3** — `plot(imp)` matplotlib trace plots; diagnostic shape matches, not pixel-identical to lattice.
- **Step 4** — `str(nhanes2)` (factor labels vs numeric codes); `plot(imp)` on `nhanes2`.
- **Step 5** — extended trace via `continue_imputation(imp3, maxit=35)` (R `mice.mids` warm start).
- **Step 6** — `stripplot()` matplotlib diagnostics; observed/imputed colours differ from lattice.

### Partial (quickpred)

- **Step 2** — `quickpred(nhanes, mincor=.3)` predictor matrix matches R golden layout."""

V03_PARITY_OVERVIEW = """\
### Expected to match exactly

These numbered steps are checked against `reference/03_missingness_inspection/vignette_extracted.R`:

- **Step 3** — `head(boys)` with R row names; `nrow(boys)` → 748; `summary(boys)` horizontal factor layout
- **Step 4** — `md.pattern(boys)` pattern matrix
- **Step 5** — `sum(mpat[,"gen"]==0)` → 8
- **Step 6** — `R <- is.na(boys$gen)` logical vector print
- **Step 9** — `help('mammalsleep')` R pager snapshot; `head(mammalsleep)` species labels; `str(mammalsleep)` layout (static reference); `summary(mammalsleep)` species counts; `md.pattern(mammalsleep)` with species column
- **Steps 10 & 13** — logged-event warnings on session mammalsleep chain (29 / 19 events; numeric `species` codes).
- **Steps 12 & 14** — `pool(fit)` / `summary(pool())` on mammalsleep (`sws ~ log10(bw) + odi`).

### Expected to differ (RNG / rendering)

- **Step 1** — package load; no R console output to compare.
- **Step 2** — `help('boys')` R pager snapshot (static reference text).

- **Step 6** — `histogram()` matplotlib panels.
- **Step 8** — `summary(complete(imp1))` on session PMM chain; `with(imp1, mean(tv))` TV means
- **Step 10** — `plot(imp)` trace lines (matplotlib vs lattice).
- **Step 15** — `plot(impnew)` convergence traces."""

V04_PARITY_OVERVIEW = """\
### Expected to match exactly

Checked against `reference/04_passive_post_processing/vignette_extracted.R`:

- **Step 2** — default `meth` and `pred` matrices; modified `pred` (exclude `ts` from `sws`/`ps`); passive `ts = sws + ps` consistency check (`pas.imp` uses `seed=123` like R)
- **Step 5** — `table(complete(imp)$tv)` and `table(complete(imp.pmm)$tv)` frequency tables (chain-aligned goldens refreshed 2026-07-05)
- **Step 7** — passive `bmi = I(wgt/(hgt/100)^2)`; numeric constraint `|bmi - calc| = 0` on missing rows (visit order imputes `hgt`/`wgt` first)

### Expected to differ (RNG / rendering)

- **Step 1** — package load; passive-imputation prose only.
- **Step 3** — `plot(pas.imp)` matplotlib trace lines.
- **Step 5** — density/histogram panels for post-squeezed `tv` (matplotlib vs lattice).
- **Steps 6–9** — `xyplot` / `plot(imp)` matplotlib diagnostics; session stream after `run_v04_chain()` (except `imp.path` `seed=123` in R).
- **Step 9** — triple-passive `sqrt(wgt/bmi)` runs; iteration event log format differs from R."""

V05_PARITY_OVERVIEW = """\
### Expected to match exactly

Checked against `reference/05_multilevel_data/golden_outputs.json` (refreshed from bundled CSV + `as.factor(class)`):

- **Step 2** — `head(popNCR)`, `dim` / `nrow` / `ncol`, `summary(popNCR)` (factor `class` layout)
- **Step 4** — full `is.na(popular)` logical vector (`width=12`, R `[1]` print)
- **Step 7** — observed ICCs for `popular`, `popteach`, `texp` on incomplete data
- **Step 8** — default `meth` / modified `meth`, `pred` matrices, `pred` with `class` and `pupil` zeroed
- **Steps 9.25, 10–12, 17, 20, 26** — ICC tables, iteration log, logged-event warnings (90 events) on session chain
- **Steps 21–24** — `pred` / `meth` setup matrices (console output only; deterministic)
- **Step 16** — `head(complete(imp2))` exact via `format_popncr_head_r` (session chain golden refreshed 2026-07-05)
- **Step 26** — logged-events warning (90 events) exact on session chain

### Expected to differ (RNG / rendering)

- **Step 1** — package load; workspace `ls()` not reproduced.
- **Steps 3, 5–6** — `md.pattern` exact; matplotlib `histogram()` panels differ from lattice.
- **Steps 13–15, 18, 22–23, 25–26** — trace / density matplotlib diagnostics.
- **Step 14** — extended traces via `continue_imputation` (R `mice.mids` warm start).

### Partial (documented tolerances)

- **Step 9.24** — imputed norm summary (atol=0.2; sex counts may differ by 1).
- **Steps 21–26 imputed values** — multilevel samplers (`2l.norm`, `2l.pan`, `2lonly.mean`, `logreg`) and PMM on `popNCR3` within moment tolerance ~0.15; setup matrices exact.
- **Step 19** — intentionally empty in R (defers ICC table to step 20)."""

V06_PARITY_OVERVIEW = """\
### Expected to match exactly

Checked against `reference/06_sensitivity_analysis/vignette_extracted.R`:

- **Step 2** — `nrow(leiden)` → 956
- **Step 3** — `mice(leiden, maxit=0)$nmis` missing-count table
- **Step 4** — `flux()` table for all variables; `md.pattern` pattern count
- **Step 6** — `delta <- c(0, -5, -10, -15, -20)`

- **Steps 11–13** — `with_mids()` + `leiden_coxph()` (lifelines strata) + `pool()`; goldens refreshed via `regenerate_v06_goldens.py` (2026-07-05)
- **Step 13** — mammalsleep δ qbar table via `run_v06_mammalsleep_delta_chain()`

### Expected to differ (RNG / rendering)

- **Step 1** — package load; no R console output to compare.
- **Step 2** — `summary(leiden)`, `head()` / `tail()` layout (R row names on `tail`; float formatting).
- **Step 4** — full `md.pattern` table whitespace; `fluxplot()` matplotlib chart.
- **Step 5** — Kaplan–Meier matplotlib curves (matplotlib equivalent).
- **Steps 7–10** — δ scenarios via `run_v06_leiden_delta_chain()` (`rng='r'`, `seed=i`); diagnostic plots for δ=0 and δ=-20."""

V07_PARITY_OVERVIEW = """\
### Expected to match exactly

These numbered steps are checked against `reference/07_ampute/vignette_extracted.R`:

- **Step 4** — `names(result)` layout for R ``mads`` objects.
- **Step 9** — `result$prop` proportion matches 0.5.
- **Step 10** — adjusted `result$prop` is 0.6 when `bycases=FALSE` and `prop=0.2`.
- **Step 11** — `mech` returns `MAR`; MNAR `patterns` layout matches R.

### Expected to differ (RNG / rendering)

- **Step 1** — package help opens R help page vs. PyMICE custom help screen.
- **Step 2** — bundled `ampute_testdata.csv`; summary may differ slightly across R versions.
- **Step 3** — MCAR `head(result$amp)`; native `run_ampute_chain()` within ~5% miss-count of R when backend unavailable.
- **Step 5** — md.pattern counts require R ``ampute`` backend (set ``PYMICE_R_AMPUTE=1``).
- **Steps 6–8** — md.pattern heatmap, bwplot, and xyplot matplotlib diagnostics.
- **Step 10** — ampute with `bycases=FALSE` cellwise proportion and adjusted `result$prop`.

### Reference-only (step 12)

The R tutorial also discusses `patterns`, `freq`, `weights`, `type`, `run`, and `odds` in depth. Step 12 documents these API sections; they are not separate R snapshot blocks.
"""

V08_PARITY_OVERVIEW = """\
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
"""
