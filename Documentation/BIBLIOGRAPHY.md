# Bibliography — MICE / FCS theoretical foundation

Primary references for the `pymice` implementation. Algorithm design follows these sources; Python code is an independent implementation.

## Core methodology

| ID | Citation | Role |
|----|----------|------|
| **JSS2011** | van Buuren, S., & Groothuis-Oudshoorn, K. (2011). *mice: Multivariate Imputation by Chained Equations in R.* Journal of Statistical Software, 45(3), 1–67. [doi:10.18637/jss.v045.i03](https://doi.org/10.18637/jss.v045.i03) | Main algorithm, API design target |
| **FCS2006** | van Buuren, S., Brand, J. P. L., Groothuis-Oudshoorn, C. G. M., & Rubin, D. B. (2006). Fully conditional specification in multivariate imputation. *Journal of Statistical Computation and Simulation*, 76(12), 1049–1064. [doi:10.1080/10629360600810434](https://doi.org/10.1080/10629360600810434) | FCS framework |
| **FIMD2018** | van Buuren, S. (2018). *Flexible Imputation of Missing Data* (2nd ed.). Chapman & Hall/CRC. [doi:10.1201/9780429492259](https://doi.org/10.1201/9780429492259) | Comprehensive treatment; online: [stefvanbuuren.name/fimd](https://stefvanbuuren.name/fimd/) |
| **RUBIN1987** | Rubin, D. B. (1987). *Multiple Imputation for Nonresponse in Surveys.* Wiley. | Pooling rules, MI inference |
| **SMMR2007** | van Buuren, S. (2007). Multiple imputation of discrete and continuous data by fully conditional specification. *Statistical Methods in Medical Research*, 16(3), 219–242. [doi:10.1177/0962280206074463](https://doi.org/10.1177/0962280206074463) | Mixed-type imputation |

## Historical / applied

| ID | Citation | Role |
|----|----------|------|
| **SIM1999** | van Buuren, S., Boshuizen, H. C., & Knook, D. L. (1999). Multiple imputation of missing blood pressure covariates in survival analysis. *Statistics in Medicine*, 18(6), 681–694. | Early MICE application |
| **SCHAfer1997** | Schafer, J. L. (1997). *Analysis of Incomplete Multivariate Data.* Chapman & Hall. | `nhanes` benchmark dataset |

## R reference implementation (behavioral target, not code copy)

| ID | Resource | License |
|----|----------|---------|
| **Rmice** | [amices/mice](https://github.com/amices/mice) CRAN 3.19.0 | GPL-2 \| GPL-3 |
| **Vignettes** | [gerkovink.com/miceVignettes](https://www.gerkovink.com/miceVignettes/) | Tutorial material (see `Vignettes/`) |
| **FIMDcode** | [stefvanbuuren/fimdbook](https://github.com/stefvanbuuren/fimdbook/tree/master/R) | Book companion scripts |

## Implementation mapping

| Concept | Primary refs | `pymice` module (planned) |
|---------|--------------|---------------------------|
| FCS / Gibbs sampler | JSS2011, FCS2006 | `pymice.engine` |
| Predictor matrix | JSS2011 | `pymice.setup` |
| PMM / norm / logreg / polyreg | JSS2011, SMMR2007 | `pymice.methods` |
| Rubin pooling | RUBIN1987, JSS2011 | `pymice.pool` |
| Convergence diagnostics | FIMD2018 Ch. 5 | `pymice.diagnostics` |
| Passive imputation | JSS2011 | `pymice.passive` |
| Multilevel | FIMD2018 Ch. 7 | `pymice.multilevel` (later) |
| Ampute (MCAR/MAR/MNAR simulation) | mice `ampute` | `pymice.ampute` (later) |