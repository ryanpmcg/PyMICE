"""Original prose from reference/01_ad_hoc_and_mice/vignette.html."""

from __future__ import annotations

import json

from lib.paths import REFERENCE_DIR
from lib.vignette_catalog import step_title

_PROSE = REFERENCE_DIR / "01_ad_hoc_and_mice" / "vignette_prose.json"

AUTHORS = "Gerko Vink and Stef van Buuren"
SERIES_LABEL = "Vignette 1 of 8"
TITLE = "Ad hoc methods and mice"

# R vignette step titles (some steps are bundled in vignette_prose.json).
STEP_TITLES: dict[int, str] = {
    1: "Open `R` and load the packages `mice` and `lattice`",
    2: "Inspect the incomplete data",
    3: "Get an overview of the data by the `summary()` command:",
    4: "Inspect the missing data pattern",
    5: "Form a regression model where `age` is predicted from `bmi`.",
    6: "Impute the missing data in the `nhanes` dataset with mean imputation.",
    7: (
        "Explore the imputed data with the `complete()` function. What do you think the "
        "variable means are? What happened to the regression equation after imputation?"
    ),
    8: "Impute the missing data in the `nhanes` dataset with regression imputation.",
    9: "Again, inspect the completed data and investigate the imputed data regression model.",
    10: "Impute the missing data in the `nhanes` dataset with stochastic regression imputation.",
    11: "Again, inspect the completed data and investigate the imputed data regression model.",
    12: (
        "Re-run the stochastic imputation model with seed `123` and verify if your "
        "results are the same as the ones below"
    ),
    13: "Let us impute the missing data in the `nhanes` dataset",
    14: "Extract the completed data",
}


def load_intro() -> str:
    data = json.loads(_PROSE.read_text(encoding="utf-8"))
    return data["intro"]


def load_step_title(num: int) -> str:
    return step_title("01", num)


# Step-specific narrative (curated from vignette.html; excludes embedded code/output).
N1_AFTER = (
    'If `mice` is not yet installed, run `install.packages("mice")` in R. '
    "PyMICE is imported directly in Python (no separate install step in this demo)."
)

N2_BEFORE = (
    "The `mice` package contains several datasets. Once the package is loaded, these datasets "
    "can be used. Have a look at the `nhanes` dataset (Schafer, 1997, Table 6.14) by typing:"
)
N2_AFTER = (
    "The `nhanes` dataset is a small data set with non-monotone missing values. It contains "
    "25 observations on four variables: *age group*, *body mass index*, *hypertension* and "
    "*cholesterol (mg/dL)*."
)
N2_HELP = "To learn more about the data, use one of the two following help commands:"

N3_BEFORE = "Get an overview of the data by the `summary()` command:"

N4_BEFORE = "Check the missingness pattern for the `nhanes` dataset"
N4_AFTER = (
    "The missingness pattern shows that there are 27 missing values in total: 10 for `chl`, "
    "9 for `bmi` and 8 for `hyp`. Moreover, there are thirteen completely observed rows, four "
    "rows with 1 missing, one row with 2 missings and seven rows with 3 missings. Looking at "
    "the missing data pattern is always useful (but may be difficult for datasets with many "
    "variables). It can give you an indication on how much information is missing and how the "
    "missingness is distributed."
)

N6_AFTER = (
    "The imputations are now done. As you can see, the algorithm ran for 1 iteration "
    "(`maxit = 1`) and presented us with only 1 imputation (`m = 1`) for each missing datum. "
    "This is correct, as substituting each missing data multiple times with the observed data "
    "mean would not make any sense (the inference would be equal, no matter which imputed "
    "dataset we would analyze). Likewise, more iterations would be computationally inefficient "
    "as the *observed* data mean does not change based on our imputations. We named the "
    "imputed object `imp` following the convention used in `mice`, but if you wish you can "
    "name it anything you'd like."
)

N7_AFTER_COMPLETE = (
    "We see the repetitive numbers `26.5625` for `bmi`, `1.2352594` for `hyp`, and `191.4` for "
    "`chl`. These can be confirmed as the means of the respective variables (columns):"
)
N7_AFTER_COLMEANS = (
    "We saw during the inspection of the missing data pattern that variable `age` has no "
    "missings. Therefore nothing is imputed for `age` because we would not want to alter the "
    "observed (and bonafide) values."
)
N7_BEFORE_POOL = "To inspect the regression model with the imputed data, run:"
N7_AFTER_POOL = (
    "It is clear that nothing changed, but then again this is not surprising as variable `bmi` "
    "is somewhat normally distributed and we are just adding weight to the mean."
)

N8_AFTER = (
    "The imputations are now done. This code imputes the missing values in the data set by the "
    'regression imputation method. The argument `method = "norm.predict"` first fits a '
    "regression model for each observed value, based on the corresponding values in other "
    "variables and then imputes the missing values with the predicted values."
)

N9_AFTER_COMPLETE = (
    "The repetitive numbering is gone. We have now obtained a more natural looking set of "
    "imputations: instead of filling in the same `bmi` for all ages, we now take `age` (as well "
    "as `hyp` and `chl`) into account when imputing `bmi`."
)
N9_BEFORE_POOL = "To inspect the regression model with the imputed data, run:"
N9_AFTER_POOL = (
    "It is clear that something has changed. In fact, we extrapolated (part of) the regression "
    "model for the observed data to missing data in `bmi`. In other words; the relation (read: "
    "information) gets stronger and we've obtained more observations."
)

N10_AFTER = (
    "The imputations are now done. This code imputes the missing values in the data set by the "
    "stochastic regression imputation method. The function does not incorporate the variability "
    "of the regression weights, so it is not 'proper' in the sense of Rubin (1987). For small "
    "samples, the variability of the imputed data will be underestimated."
)

N11_AFTER_COMPLETE = (
    "We have once more obtained a more natural looking set of imputations, where instead of "
    "filling in the same `bmi` for all ages, we now take `age` (as well as `hyp` and `chl`) "
    "into account when imputing `bmi`. We also add a random error to allow for our imputations "
    "to be off the regression line."
)
N11_BEFORE_POOL = "To inspect the regression model with the imputed data, run:"

N12_REFERENCE = """\
The R vignette shows the following pooled regression after re-running with `seed = 123`:

```text
# A tibble: 2 x 5
  term        estimate std.error statistic p.value
  <chr>          <dbl>     <dbl>     <dbl>   <dbl>
1 (Intercept)   4.13      1.13        3.66 0.00129
2 bmi          -0.0904    0.0426     -2.12 0.0449
```"""

N12_BEFORE = (
    "The imputation procedure uses random sampling, and therefore, the results will be (perhaps "
    "slightly) different if we repeat the imputations. In order to get exactly the same result, "
    "you can use the seed argument"
)
N12_AFTER = (
    "where 123 is some arbitrary number that you can choose yourself. Re-running this command "
    "will always yields the same imputed values. The ability to replicate one's findings exactly "
    "is considered essential in today's reproducible science."
)

N13_AFTER_ITER = (
    "The imputations are now done. As you can see, the algorithm ran for 5 iterations (the "
    "default) and presented us with 5 imputations for each missing datum. For the rest of this "
    "document we will omit printing of the iteration cycle when we run `mice`. We do so by "
    "adding `print=F` to the `mice` call."
)
N13_AFTER_IMP = (
    "The object `imp` contains a multiply imputed data set (of class `mids`). It encapsulates "
    "all information from imputing the `nhanes` dataset, such as the original data, the imputed "
    "values, the number of missing values, number of iterations, and so on."
)
N13_BEFORE_ATTR = (
    "To obtain an overview of the information stored in the object `imp`, use the "
    "`attributes()` function:"
)
N13_BEFORE_DATA = "For example, the original data are stored as"
N13_BEFORE_IMP = "and the imputations are stored as"

N14_BEFORE_C3 = (
    "By default, `mice()` calculates five (*m* = 5) imputed data sets. In order to get the "
    "third imputed data set, use the `complete()` function"
)
N14_BEFORE_LONG = (
    "The collection of the *m* imputed data sets can be exported by function `complete()` in "
    "long, broad and repeated formats. For example,"
)
N14_BEFORE_BROAD = "and"
