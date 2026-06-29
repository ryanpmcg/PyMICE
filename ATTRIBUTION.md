# Attribution and licensing

## Python package (`pymice`)

Copyright (c) 2026 Ryan P. McGehee and contributors.

Distributed under the **MIT License** (`LICENSE`). This is an **independent implementation** of algorithms described in the academic literature and in the R `mice` package documentation.

## Algorithm and methodology credit

The MICE / Fully Conditional Specification methodology was developed by **Stef van Buuren**, **Karin Groothuis-Oudshoorn**, and collaborators. When using this software, please cite:

1. van Buuren, S., & Groothuis-Oudshoorn, K. (2011). mice: Multivariate Imputation by Chained Equations in R. *Journal of Statistical Software*, 45(3), 1–67. https://doi.org/10.18637/jss.v045.i03

2. van Buuren, S. (2018). *Flexible Imputation of Missing Data* (2nd ed.). Chapman & Hall/CRC. https://doi.org/10.1201/9780429492259

3. Rubin, D. B. (1987). *Multiple Imputation for Nonresponse in Surveys.* John Wiley & Sons.

## R `mice` reference (GPL)

The files in `Reference/` are snapshots from [amices/mice](https://github.com/amices/mice) (GPL-2 | GPL-3). They are:

- Used **only during development** to understand expected behavior.
- **Not** included in the published Python wheel/sdist.
- **Not** translated line-for-line into `src/pymice/`.

Behavioral parity is validated via tests, not code copying.

## Vignettes (tutorial material)

The `Vignettes/` folder contains HTML and extracted R code from:

- [miceVignettes](https://www.gerkovink.com/miceVignettes/) (Gerko Vink, Stef van Buuren)
- [mice_ampute vignette](https://rianneschouten.github.io/mice_ampute/) (Rianne Schouten et al.)

These materials are stored for **reproducible verification** and are **not** redistributed as part of the installable package. Refer to the original sources for terms of use.

## No endorsement

This project is not affiliated with, endorsed by, or maintained by Stef van Buuren, TNO, or the `mice` authors. Method names (`pmm`, `midastouch`, etc.) are standard statistical terminology from the literature.

## Reproducibility

Cross-language RNG behavior and publication reporting guidance: `Documentation/REPRODUCIBILITY.md`.

## Future WEPPCLIFF integration

WEPPCLIFF (GPL-3.0-or-later) may depend on `pymice` (MIT) as an optional backend once parity is demonstrated. That integration will be documented separately in the WEPPCLIFF repository.