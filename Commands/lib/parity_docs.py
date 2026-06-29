"""Shared disclaimer and per-vignette parity overview text."""

from __future__ import annotations

GLOBAL_DISCLAIMER = """\
This page is a **PyMICE** walkthrough of the published R `mice` vignette linked above. \
It is for development verification and learning; the [original tutorial](https://www.gerkovink.com/miceVignettes/) \
remains the authoritative reference.

- **Exercise sections** below follow the same numbered order and headings as the R vignette.
- **R code** blocks are taken from `Vignettes/*/vignette_extracted.R` (snapshot of the HTML tutorial).
- **Python code** shows the PyMICE calls used to produce each output block.
- **Output** is formatted to resemble the R console; wide tables may differ slightly in whitespace.
- **Parity badges** (match / partial / skip) compare PyMICE output to the R golden text where applicable.
- PyMICE uses `seed=123` for reproducibility in several steps; the R vignette often leaves the RNG seed unset."""

V01_PARITY_OVERVIEW = """\
### Expected to match exactly

These numbered steps are deterministic and are checked against `Vignettes/01_ad_hoc_and_mice/vignette_extracted.R`:

- **Step 2** — `nhanes` row-level print
- **Step 3** — `summary(nhanes)` numeric summaries and NA counts
- **Step 4** — `md.pattern(nhanes)` pattern matrix
- **Step 5** — `lm(age ~ bmi)` on raw incomplete data (listwise deletion)
- **Step 6** — mean imputation iteration log (`method="mean"`, `m=1`, `maxit=1`)
- **Step 7** — `complete(imp)`, `colMeans(nhanes, na.rm=TRUE)`, pooled regression after mean imputation
- **Step 10** — `norm.nob` iteration log (structure only; filled values may differ — see RNG note)
- **Step 13** — default `mice(nhanes)` iteration log, `attributes(imp)`, `imp$data`
- **Step 14** — `md.pattern(complete(imp, 3))` on a fully imputed draw

### Expected to differ (RNG / rendering)

- **Step 1** — package load; no R console output to compare.
- **Step 7** — `densityplot(nhanes$bmi)` matplotlib density; diagnostic shape matches, not pixel-identical to lattice.
- **Step 11** — `complete(imp)` and pooled regression after `norm.nob` without seed (R vignette RNG).
- **Step 12** — pooled regression after `norm.nob` with `seed=123`; intercept estimate matches R, SE/p-values differ under residual sampling.
- **Step 13** — `print(imp)` structure matches; R shows seed `NA`, PyMICE reports `123`. `imp$imp` PMM values differ (unset R seed vs `seed=123`).
- **Step 14** — long and broad `complete()` layouts match R; cell values follow PMM RNG differences.

### Partial (help)

- **Step 2** — `help('nhanes')` via `pymice.help`; content differs from R pager.

### Partial (norm.predict)

- **Steps 8–9** — `norm.predict` runs in PyMICE; `complete(imp)` and pooled `lm(age ~ bmi)` use tolerance (deterministic OLS may differ slightly from R)."""

V02_PARITY_OVERVIEW = """\
### Expected to match exactly

These numbered steps are checked against `Vignettes/02_convergence_and_pooling/vignette_extracted.R`:

- **Step 2** — default and modified `pred` matrices; `maxit=0` initializer matrix
- **Step 4** — `imp$meth` on `nhanes` and `nhanes2`; `methods(mice)` listing (static reference text)
- **Step 7** — `class(fit)` and `ls(fit)` names
- **Step 8** — pooled `summary(pool.fit)` table layout (values may differ under RNG)

### Expected to differ (RNG / rendering)

- **Step 1** — `mice(nhanes, m=3)` setup; no R console output to compare.
- **Step 3** — `plot(imp)` matplotlib trace plots; diagnostic shape matches, not pixel-identical to lattice.
- **Step 4** — `summary(nhanes2)` / `str(nhanes2)` (factor labels vs numeric codes); `plot(imp)` on `nhanes2`.
- **Step 5** — `mice.mids()` not implemented; extended iteration uses fresh `mice(maxit=40)` for the plot.
- **Step 6** — `stripplot()` matplotlib diagnostics; observed/imputed colours differ from lattice.
- **Step 7** — `print(fit)` coefficient vectors and `summary(fit$analyses[[2]])` follow stochastic imputations (`seed=123`).
- **Step 8** — pooled estimates follow imputation RNG differences.

### Partial (quickpred / mice.mids)

- **Step 2** — `quickpred(nhanes, mincor=.3)` predictor matrix matches R golden layout.
- **Step 5** — `mice.mids()` not implemented; extended iteration uses fresh `mice(maxit=40)` for the plot."""

V03_PARITY_OVERVIEW = """\
### Expected to match exactly

These numbered steps are checked against `Vignettes/03_missingness_inspection/vignette_extracted.R`:

- **Step 3** — `nrow(boys)` → 748
- **Step 4** — `md.pattern(boys)` pattern matrix
- **Step 5** — `sum(mpat[,"gen"]==0)` → 8
- **Step 9** — `str(mammalsleep)` layout (static reference); `md.pattern(mammalsleep)` with species column

### Expected to differ (RNG / rendering)

- **Step 1** — package load; no R console output to compare.
- **Step 2** — `help('boys')` via `pymice.help`.
- **Step 9** — `help('mammalsleep')` via `pymice.help`.
- **Step 3** — `head(boys)` / `summary(boys)` (factor labels vs numeric codes; R row names preserved in golden text).
- **Step 6** — `histogram()` matplotlib panels; `R <- is.na(boys$gen)` truncated logical print.
- **Step 7** — `mice(boys)` imputation under `seed=123` (PMM values differ from unset R seed).
- **Step 8** — `summary(complete(imp1))` and `with(imp1, mean(tv))` follow imputation RNG.
- **Step 10** — `plot(imp)` trace lines (matplotlib vs lattice).
- **Steps 11–14** — pooled regression on `mammalsleep` (`sws ~ log10(bw) + odi`); estimates differ under RNG; table layout matches.
- **Step 15** — `plot(impnew)` convergence traces."""

V04_PARITY_OVERVIEW = """\
### Expected to match exactly

Checked against `Vignettes/04_passive_post_processing/vignette_extracted.R`:

- **Step 2** — default `meth` and `pred` matrices; modified `pred` (exclude `ts` from `sws`/`ps`); passive `ts = sws + ps` consistency check
- **Step 5** — `table(complete(imp.pmm)$tv)` frequency table (under `seed=123`)

### Expected to differ (RNG / rendering)

- **Step 1** — package load; passive-imputation prose only.
- **Step 3** — `plot(pas.imp)` matplotlib trace lines.
- **Steps 4–5** — `post` + `squeeze(1, 25)` on `tv` with `norm`; table and density diagnostics under `seed=123`.
- **Steps 6–9** — `xyplot` / `plot(imp)` matplotlib diagnostics; boys passive `bmi` imputations under `seed=123`.
- **Steps 4–5** — `post_squeeze(1, 25)` on `tv` with `norm` under `seed=123`.
- **Step 9** — pathological triple-passive with `sqrt()` not run (parser limitation); iteration log shown as reference."""

V05_PARITY_OVERVIEW = """\
### Expected to match exactly

Checked against `Vignettes/05_multilevel_data/vignette_extracted.R`:

- **Step 2** — `head(popNCR)`, `dim` / `nrow` / `ncol`
- **Step 7** — observed ICCs for `popular`, `popteach`, `texp` on incomplete data
- **Step 8** — default `meth` / modified `meth`, `pred` matrices, `pred` with `class` and `pupil` zeroed

### Expected to differ (RNG / rendering)

- **Step 1** — package load; workspace `ls()` not reproduced (bundled `popNCR.csv`).
- **Step 2** — `summary(popNCR)` (`class` factor labels vs numeric codes).
- **Steps 3–6** — `md.pattern` layout; truncated `is.na()` print; matplotlib `histogram()` panels.
- **Steps 9–12, 16–20** — `norm` / `pmm` imputations under `seed=123` (R vignette also uses `set.seed(123)` but PMM/norm draws differ); ICC and `complete()` tables use tolerance.
- **Steps 13–15, 17–18** — trace / density matplotlib diagnostics.
- **Step 14** — `mice.mids()` not implemented; extended trace via fresh `mice(maxit=15)`.

### Partial (multilevel methods)

- **Steps 21–25** — `2l.norm`, `2l.pan`, and `2lonly.mean` on bundled `popNCR2` / `popNCR3`; imputation values differ under RNG. Full multilevel Gibbs via `jomoImpute` / `panImpute` (Phase 7a).
- **Step 26** — `pmm` on `popNCR3` (partial; numeric `class` coding).

### Not yet implemented (skipped)

- **Step 19** — `orig` ICC column from complete `popular` dataset (not bundled)."""

V06_PARITY_OVERVIEW = """\
### Expected to match exactly

Checked against `Vignettes/06_sensitivity_analysis/vignette_extracted.R`:

- **Step 2** — `nrow(leiden)` → 956
- **Step 3** — `mice(leiden, maxit=0)$nmis` missing-count table
- **Step 4** — `flux()` table for all variables; `md.pattern` pattern count
- **Step 6** — `delta <- c(0, -5, -10, -15, -20)`

### Expected to differ (RNG / rendering)

- **Step 1** — package load; no R console output to compare.
- **Step 2** — `summary(leiden)`, `head()` / `tail()` layout (R row names on `tail`; float formatting).
- **Step 4** — full `md.pattern` table whitespace; `fluxplot()` matplotlib chart.
- **Step 5** — Kaplan–Meier matplotlib curves (matplotlib equivalent; Cox PH not in PyMICE).
- **Steps 7–10** — δ-adjustment via `post_add` creating `imp_all`; diagnostic plots for δ=0 and δ=-20.
- **Step 13** — mammalsleep passive `ts` + `post_add` on `sws`; pooled `lm(sws ~ log10(bw) + odi)` qbar table under RNG tolerance.

### Not yet implemented (skipped)

- **Steps 11–12** — `with()` + `coxph()` + `pool()` on delta scenarios (Cox PH / survival not in PyMICE)."""
