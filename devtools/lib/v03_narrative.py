"""Original prose from reference/03_missingness_inspection/vignette.html."""

from __future__ import annotations

import json

from lib.paths import REFERENCE_DIR
from lib.vignette_catalog import step_title

_PROSE = REFERENCE_DIR / "03_missingness_inspection" / "vignette_prose.json"

AUTHORS = "Gerko Vink and Stef van Buuren"
SERIES_LABEL = "Vignette 3 of 8"
TITLE = "`mice`: The imputation and nonresponse models"

STEP_TITLES: dict[int, str] = {
    1: "Open `R` and load the packages `mice` and `lattice`. Also, fix the random seed.",
    2: (
        "The `boys` dataset is part of `mice`. It is a subset of a large Dutch dataset "
        "containing growth measures from the Fourth Dutch Growth Study. Inspect the help for "
        "`boys` dataset and make yourself familiar with its contents."
    ),
    3: (
        "Get an overview of the data. Find information about the size of the data, the "
        "variables measured and the amount of missingness."
    ),
    4: (
        "As we have seen before, the function `md.pattern()` can be used to display all "
        "different missing data patterns. How many different missing data patterns are present "
        "in the boys dataframe and which pattern occurs most frequently in the data?"
    ),
    5: "How many patterns occur for which the variable `gen` (genital Tannerstage) is missing?",
    6: (
        "Let us focus more precisely on the missing data patterns. Does the missing data of "
        "`gen` depend on `age`? One could for example check this by making a histogram of `age` "
        "separately for the cases with known genital stages and for cases with missing genital stages."
    ),
    7: (
        "Impute the `boys` dataset with mice using all default settings and name the `mids` "
        "(multiply imputed data set) object `imp1`."
    ),
    8: (
        "Compare the means of the imputed data with the means of the incomplete data. One can use "
        "the function `complete()` with a `mids`-object as argument to obtain an imputed dataset. "
        "As default, the first imputed dataset will be given by this function."
    ),
    9: (
        "Get an overview of the data. Find information about the size of the data, the variables "
        "measured and the amount of missingness."
    ),
    10: "Generate five imputed datasets with the default method `pmm`. Give the algorithm 10 iterations.",
    11: (
        "Perform a regression analysis on the imputed dataset with `sws` as dependent variable "
        "and `log(bw)` and `odi` as independent variables."
    ),
    12: "Pool the regression analysis and inspect the pooled analysis.",
    13: "Impute `mammalsleep` again, but now exclude `species` from the data. Name the new imputed dataset `impnew`.",
    14: "Compute and pool the regression analysis again.",
    15: "Plot the trace lines for `impnew`",
}

PART_IMPORTANCE = "The importance of the imputation model"

N1_AFTER = (
    "We choose seed value `123`. This is an arbitrary value; any value would be an equally good "
    "seed value. Fixing the random seed enables you (and others) to exactly replicate anything "
    "that involves random number generators. If you set the seed in your `R` instance to `123`, "
    "you will get the exact same results and plots as we present in this document."
)

N2_HELP = (
    "To learn more about the contents of the data, use one of the two following help commands:"
)

N4_AFTER = (
    "There are 13 patterns in total, with the pattern where `gen`, `phb` and `tv` are missing "
    "occuring the most."
)

N5_AFTER = "Answer: 8 patterns (503 cases)"

N6_BEFORE_IND = (
    "To create said histogram in `R`, a missingness indicator for `gen` has to be created. "
    "A missingness indicator is a dummy variable with value `1` for observed values (in this case "
    "genital status) and `0` for missing values. Create a missingness indicator for `gen` by typing"
)
N6_AFTER_IND = (
    "As we can see, the missingness indicator tells us for each value in `gen` whether it is "
    "missing (`TRUE`) or observed (`FALSE`)."
)
N6_BEFORE_HIST = "A histogram can be made with the function `histogram()`."
N6_HIST_EQUIV = (
    "or, equivalently, one could use\n\n"
    "`histogram(~ gen, data = boys)`\n\n"
    "Writing the latter line of code for plots is more efficient than selecting every part of the "
    "`boys` data with the `boys$...` command, especially if plots become more advanced. The code "
    "for a conditional histogram of `age` given `R` is"
)
N6_AFTER_HIST = (
    "The histogram shows that the missingness in `gen` is not equally distributed across `age`."
)

N8_AFTER_SUMMARY = (
    "Most means are roughly equal, except the mean of `tv`, which is much lower in the first "
    "imputed data set, when compared to the incomplete data. This makes sense because most genital "
    "measures are unobserved for the lower ages. When imputing these values, the means should decrease."
)
N8_BEFORE_WITH = (
    "Investigating univariate properties by using functions such as `summary()`, may not be ideal "
    "in the case of hundreds of variables. To extract just the information you need, for all "
    "imputed datasets, we can make use of the `with()` function. To obtain summaries for each "
    "imputed `tv` only, type"
)

N9_BEFORE_MS = (
    "The `mammalsleep` dataset is part of `mice`. It contains the Allison and Cicchetti (1976) "
    "data for mammalian species. To learn more about this data, type"
)
N9_AFTER_MDP = (
    "Answer: 8 patterns in total, with the pattern where everything is observed occuring the most "
    "(42 times)."
)

N10_AFTER_IMP = "Inspect the trace lines"
N12_AFTER_POOL = (
    "The `fmi` and `lambda` are much too high. This is due to `species` being included in the "
    "imputation model. Because there are 62 species and mice automatically converts factors "
    "(categorical variables) to dummy variables, each species is modeled by its own imputation model."
)
N14_AFTER_POOL = (
    "Note that the `fmi` and `lambda` have dramatically decreased. The imputation model has been "
    "greatly improved."
)

N15_AFTER = (
    "Even though the fraction of information missing due to nonresponse (fmi) and the relative "
    "increase in variance due to nonresponse (lambda) are nice and low, the convergence turns out "
    "to be a real problem. The reason is the structure in the data. Total sleep (`ts`) is the sum "
    "of paradoxical sleep (`ps`) and short wave sleep (`sws`). This relation is ignored in the "
    "imputations, but it is necessary to take this relation into account. `mice` offers a routine "
    "called passive imputation, which allows users to take transformations, combinations and "
    "recoded variables into account when imputing their data.\n\n"
    "We explain passive imputation in detail in the this vignette.\n\n"
    "We have seen that the practical execution of multiple imputation and pooling is "
    "straightforward with the `R` package `mice`. The package is designed to allow you to assess "
    "and control the imputations themselves, the convergence of the algorithm and the distributions "
    "and multivariate relations of the observed and imputed data.\n\n"
    "It is important to ‘gain’ this control as a user. After all, we are imputing values and we "
    "aim to properly adress the uncertainty about the missingness problem.\n\n"
    "**- End of Vignette**"
)


def load_intro() -> str:
    data = json.loads(_PROSE.read_text(encoding="utf-8"))
    return data["intro"]


def load_step_title(num: int) -> str:
    return step_title("03", num)
