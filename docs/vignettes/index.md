# PyMICE vignette report

Generated: 2026-07-07T22:33:40.167558+00:00

## Vignettes

| # | Title | Status | Report |
|---|-------|--------|--------|
| V1 | Ad Hoc MICE | Partially compliant — 24 match, 1 info, 2 partial, 0 skipped (R-only) | [v01_ad_hoc_mice.md](v01_ad_hoc_mice.md) / [HTML](v01_ad_hoc_mice.html) |
| V2 | Convergence Pooling | Partially compliant — 16 match, 5 info, 5 partial, 0 skipped (R-only) | [v02_convergence_pooling.md](v02_convergence_pooling.md) / [HTML](v02_convergence_pooling.html) |
| V3 | Missingness Models | Non-compliant — 7 mismatches, 13 match, 0 skip, 7 partial | [v03_missingness.md](v03_missingness.md) / [HTML](v03_missingness.html) |
| V4 | Passive Imputation | Partially compliant — 8 match, 5 info, 10 partial, 0 skipped (R-only) | [v04_passive.md](v04_passive.md) / [HTML](v04_passive.html) |
| V5 | Multilevel Data | Partially compliant — 23 match, 5 info, 27 partial, 1 skipped (R-only) | [v05_multilevel.md](v05_multilevel.md) / [HTML](v05_multilevel.html) |
| V6 | Sensitivity Analysis | Partially compliant — 9 match, 2 info, 11 partial, 0 skipped (R-only) | [v06_sensitivity.md](v06_sensitivity.md) / [HTML](v06_sensitivity.html) |
| V7 | Ampute Simulation | Partially compliant — 10 match, 1 info, 2 partial, 2 skipped (R-only) | [v07_ampute.md](v07_ampute.md) / [HTML](v07_ampute.html) |
| V8 | Parallel MICE | Partially compliant — 5 match, 5 info, 1 partial, 1 skipped (R-only) | [v08_futuremice.md](v08_futuremice.md) / [HTML](v08_futuremice.html) |

## Test suite (pytest)

```text
........................................................................ [ 28%]
........................................................................ [ 56%]
........................................................................ [ 84%]
........................................                                 [100%]
============================== warnings summary ===============================
tests/unit/test_convergence.py::test_convergence_returns_rows_per_variable_iteration
tests/unit/test_quickpred.py::test_quickpred_nhanes_mincor_03
  C:\Python-3-13\Lib\site-packages\numpy\lib\_function_base_impl.py:3065: RuntimeWarning: invalid value encountered in divide
    c /= stddev[:, None]

tests/unit/test_jomo_extended.py::test_2lonly_mean_class_mean_and_empty_class
  C:\Users\Ryan McGehee\PyMICE\src\pymice\methods\twolonly_mean.py:75: RuntimeWarning: Mean of empty slice
    [np.nanmean(agg_y[agg_classes == c]) for c in agg_classes],

tests/unit/test_jomo_extended.py::test_imp8_class_factor_pmm_smoke
  C:\Users\Ryan McGehee\PyMICE\src\pymice\methods\logreg.py:79: RuntimeWarning: overflow encountered in exp
    prob = 1.0 / (1.0 + np.exp(-eta))

tests/unit/test_jomo_extended.py::test_imp8_class_factor_pmm_smoke
  C:\Users\Ryan McGehee\PyMICE\tests\unit\test_jomo_extended.py:287: RuntimeWarning: Number of logged events: 12
    result = mice(

tests/unit/test_logreg_polyreg.py::test_mice_with_explicit_factor_specs
  C:\Users\Ryan McGehee\PyMICE\tests\unit\test_logreg_polyreg.py:54: RuntimeWarning: Number of logged events: 12
    result = mice(

tests/unit/test_postprocess.py::test_post_squeeze_in_mice
  C:\Users\Ryan McGehee\PyMICE\src\pymice\engine.py:521: RuntimeWarning: Mean of empty slice
    chain_mean[name][k2, :] = np.nanmean(imp[name], axis=0)

tests/unit/test_postprocess.py::test_post_squeeze_in_mice
  C:\Users\Ryan McGehee\PyMICE\src\pymice\engine.py:522: RuntimeWarning: Degrees of freedom <= 0 for slice.
    chain_var[name][k2, :] = np.nanvar(imp[name], axis=0)

tests/unit/test_postprocess.py::test_post_squeeze_in_mice
  C:\Users\Ryan McGehee\PyMICE\tests\unit\test_postprocess.py:19: RuntimeWarning: Number of logged events: 2
    result = mice(

tests/unit/test_pythonic_api.py::test_verbose_and_max_iter_aliases
  C:\Users\Ryan McGehee\PyMICE\tests\unit\test_pythonic_api.py:31: DeprecationWarning: max_iter is deprecated; use maxit=
    result = mice(data, column_names=names, m=1, max_iter=1, verbose=False, seed=1)

tests/unit/test_pythonic_api.py::test_verbose_and_max_iter_aliases
  C:\Users\Ryan McGehee\PyMICE\tests\unit\test_pythonic_api.py:31: DeprecationWarning: verbose is deprecated; use print=False
    result = mice(data, column_names=names, m=1, max_iter=1, verbose=False, seed=1)

tests/unit/test_pythonic_api.py::test_mids_summary_and_continue
  C:\Users\Ryan McGehee\PyMICE\src\pymice\types.py:185: DeprecationWarning: max_iter is deprecated; use maxit=
    return continue_imputation(

tests/unit/test_pythonic_api.py::test_mids_summary_and_continue
  C:\Users\Ryan McGehee\PyMICE\src\pymice\types.py:185: DeprecationWarning: verbose is deprecated; use print=False
    return continue_imputation(

tests/unit/test_pythonic_api.py::test_continue_imputation_function
  C:\Users\Ryan McGehee\PyMICE\tests\unit\test_pythonic_api.py:100: DeprecationWarning: max_iter is deprecated; use maxit=
    more = continue_imputation(base, max_iter=2)

tests/unit/test_pythonic_api.py::test_mice_df
  C:\Users\Ryan McGehee\PyMICE\tests\unit\test_pythonic_api.py:129: DeprecationWarning: mice_df() is deprecated; use mice(df, ...) instead
    result = mice_df(df, m=1, maxit=1, seed=9)

tests/unit/test_quickpred.py::test_quickpred_nhanes_mincor_03
  C:\Python-3-13\Lib\site-packages\numpy\lib\_function_base_impl.py:3066: RuntimeWarning: invalid value encountered in divide
    c /= stddev[None, :]

tests/unit/test_r_gaps_implemented.py::test_cbind_and_rbind_mids
  C:\Users\Ryan McGehee\PyMICE\tests\unit\test_r_gaps_implemented.py:58: RuntimeWarning: Number of logged events: 2
    imp1 = mice(

tests/unit/test_r_gaps_implemented.py::test_cbind_and_rbind_mids
  C:\Users\Ryan McGehee\PyMICE\tests\unit\test_r_gaps_implemented.py:64: RuntimeWarning: Number of logged events: 4
    imp2 = mice(

tests/unit/test_rf.py::test_mice_runs_with_rf_method
  C:\Users\Ryan McGehee\PyMICE\tests\unit\test_rf.py:82: RuntimeWarning: Number of logged events: 4
    result = mice(

tests/unit/test_survival.py::test_leiden_coxph_matches_r_complete_data[C(sbpgp, contr.treatment(6, base = 3))1]
tests/unit/test_survival.py::test_leiden_coxph_matches_r_complete_data[C(sbpgp, contr.treatment(6, base = 3))2]
  C:\Python-3-13\Lib\site-packages\lifelines\fitters\__init__.py:1284: FutureWarning: The default of observed=False is deprecated and will be changed to True in a future version of pandas. Pass observed=False to retain current behavior or observed=True to adopt the future default and silence this warning.
    for stratum, df_ in df.groupby(strata):

tests/unit/test_survival.py::test_leiden_coxph_matches_r_complete_data[C(sbpgp, contr.treatment(6, base = 3))1]
tests/unit/test_survival.py::test_leiden_coxph_matches_r_complete_data[C(sbpgp, contr.treatment(6, base = 3))1]
tests/unit/test_survival.py::test_leiden_coxph_matches_r_complete_data[C(sbpgp, contr.treatment(6, base = 3))1]
tests/unit/test_survival.py::test_leiden_coxph_matches_r_complete_data[C(sbpgp, contr.treatment(6, base = 3))1]
tests/unit/test_survival.py::test_leiden_coxph_matches_r_complete_data[C(sbpgp, contr.treatment(6, base = 3))2]
tests/unit/test_survival.py::test_leiden_coxph_matches_r_complete_data[C(sbpgp, contr.treatment(6, base = 3))2]
tests/unit/test_survival.py::test_leiden_coxph_matches_r_complete_data[C(sbpgp, contr.treatment(6, base = 3))2]
tests/unit/test_survival.py::test_leiden_coxph_matches_r_complete_data[C(sbpgp, contr.treatment(6, base = 3))2]
  C:\Python-3-13\Lib\site-packages\lifelines\fitters\coxph_fitter.py:1868: FutureWarning: The default of observed=False is deprecated and will be changed to True in a future version of pandas. Pass observed=False to retain current behavior or observed=True to adopt the future default and silence this warning.
    for stratum, stratified_X in X.groupby(self.strata):

tests/unit/test_survival.py::test_leiden_coxph_matches_r_complete_data[C(sbpgp, contr.treatment(6, base = 3))1]
tests/unit/test_survival.py::test_leiden_coxph_matches_r_complete_data[C(sbpgp, contr.treatment(6, base = 3))2]
  C:\Python-3-13\Lib\site-packages\lifelines\fitters\coxph_fitter.py:2538: FutureWarning: The default of observed=False is deprecated and will be changed to True in a future version of pandas. Pass observed=False to retain current behavior or observed=True to adopt the future default and silence this warning.
    for name, stratum_predicted_partial_hazards_ in predicted_partial_hazards_.groupby(self.strata):

tests/vignettes/test_02_tier_a_methods.py::test_where_mask_limits_imputation
  C:\Users\Ryan McGehee\PyMICE\tests\vignettes\test_02_tier_a_methods.py:109: RuntimeWarning: Number of logged events: 2
    result = mice(data, column_names=["a", "b"], method="mean", m=1, maxit=1, where=where, seed=1)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
```
