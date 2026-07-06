---
title: 'PyMICE: A Python Package for Multivariate Imputation by Chained Equations with R Alignment'
tags:
  - Python
  - statistics
  - missing data
  - multiple imputation
  - fully conditional specification
authors:
  - name: Ryan P. McGehee
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 29 June 2026
bibliography: paper.bib
---

# Summary

Missing data is a pervasive challenge across scientific disciplines, including medicine, epidemiology, social sciences, and engineering. When data are not missing completely at random (MCAR), standard ad-hoc approaches like complete-case analysis (dropping rows with missing values) or single mean imputation introduce significant parameter bias, underestimate statistical uncertainty, and distort relationships between variables.

Multiple Imputation (MI) under Fully Conditional Specification (FCS)---commonly referred to as Multivariate Imputation by Chained Equations (MICE)---is the gold-standard method for addressing missing data [@rubin1987multiple; @vanbuuren2018flexible]. `PyMICE` is a clean-room, standalone Python library that replicates the behavior, methods, and diagnostics of the reference R `mice` package [@vanbuuren2011mice] in a native Python ecosystem. It provides researchers with a robust, MIT-licensed tool to perform imputation, fit repeated-imputation models, and pool estimates according to Rubin's rules.

# Statement of Need

Historically, the R package `mice` [@vanbuuren2011mice] has served as the de facto standard implementation of Fully Conditional Specification. While Python is now the dominant language for data science and machine learning, its ecosystem has lacked a fully compliant multiple imputation library. 

Existing Python alternatives are limited:
*   `scikit-learn`'s `IterativeImputer` [@pedregosa2011scikit] is designed primarily for predictive pipelines rather than statistical inference. It is limited to single imputations, lacks stochastic noise drawing, and does not support pooling (Rubin's rules) or convergence diagnostics.
*   Other libraries either lack support for complex variable types (e.g., binary or categorical variables) or do not match the statistical behaviors of R's reference implementation.

`PyMICE` bridges this gap by delivering:
1.  **Algorithmic Parity:** A Python engine implementing 35 imputation methods matching the R `methods(mice)` surface, including Predictive Mean Matching (`pmm`), Bayesian OLS (`norm`), logistic regression (`logreg`), multilevel models (`2l.norm`, `2l.pan`, `2l.lmer`), JOMO multivariate blocks (`jomoImpute`), and sensitivity methods (`mnar`, `ri`).
2.  **Rubin's Rules Pooling:** Automatic compilation of Multiple Imputation Repeated Analysis (`mira`) and Pooling (`mipo`) to compute pooled coefficients, standard errors, fraction of missing information (FMI), and adjusted degrees of freedom [@rubin1987multiple].
3.  **Advanced Diagnostic Visualizations:** Convergence monitoring (mean and variance trace plots) and density comparison plots utilizing Gaussian kernel density estimation (KDE) and rug indicators, matching R's lattice-based diagnostic plots.
4.  **Data Amputation:** Native and optional R-backed implementations of the `ampute` algorithm for simulating multivariate missingness under MCAR, MAR, and MNAR mechanisms.
5.  **Parallel Imputation:** `futuremice()` distributes imputations across worker processes with reproducible `parallelseed` metadata, matching the R `futuremice` workflow.
6.  **Cross-Language Validation:** Eight R tutorial vignettes (V01–V08) drive structural and RNG parity tests; optional `rng="r"` enables bit-identical imputations where required.

# Core Software Architecture

`PyMICE` is organized as a modular package with minimal dependencies, relying only on `NumPy` and `SciPy` for its core computation, and `Matplotlib` for optional visualization:

*   **`pymice.engine`**: Chained-equation Gibbs sampler with visit sequences, blocks, passive formulas, and post-processing hooks.
*   **`pymice.imputation_setup`**: Predictor matrices, method defaults, `quickpred`, and block construction.
*   **`pymice.methods`**: 35 registered univariate and multivariate imputation algorithms with optional R (`lme4`, `pan`) and scikit-learn backends.
*   **`pymice.pool`**: Rubin's rules pooling for linear, GLM, and Cox model fits across $m$ imputations.
*   **`pymice.parallel`**: `futuremice` / `parallel_mice` with `ProcessPoolExecutor` and `ibind` merge.
*   **`pymice.ampute`**: MCAR/MAR/MNAR missingness simulation with optional R backend.
*   **`pymice.diagnostics`**: `md.pattern`, `flux`, and matplotlib diagnostic plots.
*   **`pymice.rng`**: Pluggable RNG backends (`numpy`, `legacy`, `r`) for independent or R-matched stochastic draws.

# Simulation Study

To demonstrate the correctness and utility of `PyMICE`, we run a Monte Carlo simulation study comparing three imputation strategies on a simulated dataset ($N = 500$) with Missing at Random (MAR) values (30% missingness in predictors). The true model is:

$$Y = 2.0 + 1.5 X_1 - 0.8 X_2 + \epsilon, \quad \epsilon \sim N(0, 1)$$

We run 50 trials, imputing missing data with $m = 5$ imputations, and fit the linear model $Y \sim X_1 + X_2$. We evaluate parameter bias, average standard errors, and the coverage rate of the nominal 95% confidence intervals (CI) for the coefficient $\beta_1$ (true value = 1.5).

Table 1 outlines the results:

| Imputation Method | Mean Est. | Bias | Avg. SE | 95% CI Coverage |
|:------------------|:---------:|:----:|:-------:|:---------------:|
| Mean Imputation | 1.0481 | -0.4519 | 0.0624 | 0.0% |
| Regression (`norm.predict`) | 1.5998 | +0.0998 | 0.0395 | 44.0% |
| **PMM (`pmm`)** | **1.4738** | **-0.0262** | **0.0635** | **92.0%** |

*Table 1: Parameter recovery and nominal 95% CI coverage for $\beta_1$ across 50 simulation trials.*

As expected theoretically [@vanbuuren2018flexible]:
*   **Mean Imputation** severely biases the coefficient estimate toward zero (attenuation bias) and yields 0% coverage.
*   **Regression Imputation** (`norm.predict`) recovers the coefficient but underestimates the variance, causing standard errors to be too narrow and resulting in a confidence interval coverage of only 44.0% (nominal is 95%).
*   **Predictive Mean Matching (`pmm`)** successfully recovers the parameter with negligible bias and achieves a 92.0% coverage rate, verifying the correct propagation of imputation uncertainty by `PyMICE`.

The simulation results can be reproduced by running the script `Demonstration/simulation_study.py`.

# Acknowledgements

We acknowledge Stef van Buuren and the upstream R `mice` developers, whose theoretical foundations and library design made this project possible.

# References
