"""Original prose from reference/05_multilevel_data/vignette.html."""

from __future__ import annotations

import json

from lib.paths import REFERENCE_DIR
from lib.vignette_catalog import step_title

_PROSE = REFERENCE_DIR / "05_multilevel_data" / "vignette_prose.json"

AUTHORS = "Gerko Vink and Stef van Buuren"
SERIES_LABEL = "Vignette 5 of 8"
TITLE = "`mice`: Imputing multi-level data"

PART_INSPECTION = "Inspection of the incomplete data"
PART_CONVERGENCE = "Checking Convergence of the imputations"

STEP_TITLES: dict[int, str] = {
    1: "Open `R` and load the packages `mice`, `lattice` and `pan`.",
    2: (
        "Check with the functions `head()`, `dim()` - alternatively one could use `nrow()` "
        "and `ncol()` instead of `dim()` - and `summary()` how large the dataset is, of which "
        "variables the data frame consists and if there are missing values in a variable."
    ),
    3: (
        "As we have seen before, the function `md.pattern()` is used to display all different "
        "missing data patterns. How many different missing data patterns are present in the "
        "`popNCR` dataframe and which patterns occur most frequently in the data? Also find out "
        "how many patterns we would observe when variable `texp` (teacher experience) is not "
        "considered."
    ),
    4: (
        "Let's focus more precisely on the missing data patterns. Does the missing data of "
        "`popular` depend on `popteach`? One could for example check this by making a histogram "
        "of `popteach` separately for the pupils with known popularity and missing popularity."
    ),
    5: (
        "Does the missingness of the other incomplete variables depend on `popteach`? If yes, "
        "what is the direction of the relation?"
    ),
    6: "Find out if the missingness in teacher popularity depends on pupil popularity.",
    7: (
        "Have a look at the intraclass correlation (ICC) for the incomplete variables "
        "`popular`, `popteach` and `texp`."
    ),
    8: (
        "Impute the `popNCR` dataset with `mice` using imputation method `norm` for "
        "`popular`, `popteach`, `texp` and `extrav`. Exclude `class` as a predictor "
        "*for all variables*. Call the `mids`-object `imp1`."
    ),
    9: (
        "Compare the means of the variables in the first imputed dataset and in the "
        "incomplete dataset."
    ),
    10: (
        "Compare the ICCs of the variables in the first imputed dataset with those in the "
        "incomplete dataset (use `popular`, `popteach` and `texp`). Make a notation of the "
        "ICCs after imputation."
    ),
    11: (
        "Now impute the `popNCR` dataset again with `mice` using imputation method `norm` for "
        "`popular`, `popteach`, `texp` and `extrav`, but now include `class` as a predictor "
        "*for all variables*. Call the `mids`-object `imp2`."
    ),
    12: (
        "Compare the ICCs of the variables in the first imputed dataset from `imp2` with those "
        "of `imp1` and the incomplete dataset (use `popular`, `popteach` and `texp`). Make a "
        "notation of the ICCs after imputation."
    ),
    13: ("Inspect the trace lines for the variables `popular`, `texp` and `extrav`."),
    14: (
        "Add another 10 iterations and inspect the trace lines again. What do you observe with "
        "respect to the convergence of the sampler?"
    ),
    15: (
        "Plot the densities of the observed and imputed data (use `imp2`) with the function "
        "`densityplot()`."
    ),
    16: (
        "Have a look at the imputed dataset by asking the first 15 rows of the first completed "
        "dataset for `imp2`. What do you think of the imputed values?"
    ),
    17: (
        "Impute the `popNCR` data once more where you use predictive mean matching and include "
        "all variables as predictors. Name the object `imp4`."
    ),
    18: (
        "Plot again the densities of the observed and imputed data with the function "
        "`densityplot()`, but now use `imp4`. Is there a difference between the imputations "
        "obtained with `pmm` and `norm` and can you explain this?"
    ),
    19: (
        "Compare the ICCs of the variables in the first imputed dataset from `imp4` with those "
        "of `imp1`, `imp2` and the incomplete dataset (use `popular`, `popteach` and `texp`)."
    ),
    20: (
        "Finally, compare the ICCs of the imputations to the ICCs in the original data. The "
        "original data can be found in dataset `popular`. What do you conclude?"
    ),
    21: ("Impute the variable `popular` by means of `2l.norm`. Use dataset `popNCR2`."),
    22: "Inspect the imputations. Did the algorithm converge?",
    23: (
        "In the original data, the group variances for `popular` are homogeneous. Use `2l.pan` "
        "to impute the variable `popular` in dataset `popNCR2`. Inspect the imputations. Did "
        "the algorithm converge?"
    ),
    24: (
        "Now inspect dataset `popNCR3` and impute the incomplete variables according to the "
        "following imputation methods:"
    ),
    25: ("Evaluate the imputations by means of convergence, distributions and plausibility."),
    26: ("Repeat the same imputations as in the previous step, but now use `pmm` for everything."),
}

N1_AFTER = (
    "We choose seed value `123`. This is an arbitrary value; any value would be an equally good "
    "seed value. Fixing the random seed enables you (and others) to exactly replicate anything "
    "that involves random number generators. If you set the seed in your `R` instance to `123`, "
    "you will get the exact same results and plots as we present in this document.\n\n"
    "We are going to work with the popularity data from Joop Hox (2010). The variables in this "
    "data set are described as follows:"
)

N2_AFTER = (
    "The data set has 2000 rows and 7 columns (variables). The variables `extrav`, `sex`, "
    "`texp`, `popular` and `popteach` contain missings. About a quarter of these variables is "
    "missing, except for `texp` where 50 % is missing."
)

N3_AFTER = (
    "There are 32 unique patterns. The pattern where everything is observed and the pattern "
    "where only texp is missing occur most frequently.\n\n"
    "If we omit texp, then the following pattern matrix is realized:\n\n"
    "Without texp, there are only 16 patterns."
)

N4_BEFORE_IND = (
    "In R the missingness indicator\n\n"
    "`is.na(popNCR$popular)`\n\n"
    "can be used to create a dummy variable for the missingness in `popular`. "
    "Alternatively, one can use the missingness indicator directly in a formula "
    "(as we will do below).\n\n"
    "Does the missing data of `popular` depend on `popteach`? One could for example check "
    "this by making a histogram of `popteach` separately for the pupils with known "
    "popularity and missing popularity."
)
N4_AFTER_HIST = (
    "The histogram shows that the missingness in `popular` is not equally distributed across "
    "`popteach`. The missingness in `popular` is right-tailed."
)

N5_AFTER = (
    "There seems to be a left-tailed relation between `popteach` and the missingness in `sex`.\n\n"
    "There also seems to be a left-tailed relation between `popteach` and the missingness in "
    "`extrav`.\n\n"
    "There seems to be no observable relation between `popteach` and the missingness in `texp`. "
    "It might be MCAR or even MNAR."
)

N6_AFTER = "Yes: there is a dependency. The relation seems to be right-tailed."

N7_AFTER = (
    "Please note that the function `icc()` comes from the package `multilevel` (function "
    "`ICC1()`), but is included in the workspace `popular.RData`. Write down the ICCs, you'll "
    "need them later.\n\n"
    "**7b. Do you think it is necessary to take the multilevel structure into account?**\n\n"
    "YES! There is a strong cluster structure going on. If we ignore the clustering in our "
    "imputation model, we may run into invalid inference. To stay as close to the true data "
    "model, we must take the cluster structure into account during imputation."
)

N9_AFTER = (
    "**9b. The missingness in `texp` is MNAR: higher values for `texp` have a larger "
    "probability to be missing. Can you see this in the imputed data? Do you think this is a "
    "problem?**\n\n"
    "Yes, we can see this in the imputed data: teacher experience increases slightly after "
    "imputation. However, `texp` is the same for all pupils in a class. But not all pupils have "
    "this information recorded (as if some pupils did not remember, or were not present during "
    "data collection). This is not a problem, because as long as at least one pupil in each "
    "class has teacher experience recorded, we can deductively impute the correct (i.e. true) "
    "value for every pupil in the class."
)

N12_AFTER = (
    "By simply forcing the algorithm to use the class variable during estimation we adopt a "
    "*fixed effects approach*. This conforms to formulating seperate regression models for each "
    "`class` and imputing within classes from these models."
)

N14_AFTER = (
    "It seems OK. Adding another 20 iterations confirms this.\n\n"
    "**Further inspection**\n\n"
    "Several plotting methods based on the package `lattice` for Trellis graphics are "
    "implemented in `mice` for imputed data."
)

N15_BEFORE = (
    "To obtain all densities of the different imputed datasets use\n\n"
    "`densityplot(imp2)`\n\n"
    "To obtain just the densities for popular one can use\n\n"
    "`densityplot(imp2, ~ popular)`\n\n"
    "or"
)
N15_AFTER = (
    "The latter case results in a conditional plot (conditional on the different imputed datasets)."
)

N18_AFTER = (
    "Yes, `pmm` samples from the observed values and this clearly shows: imputations follow "
    "the shape of the observed data."
)

N19_DEFER = "See **Exercise 20** for the solution."

N20_AFTER = (
    "Note: these display only the first imputed data set.\n\n"
    "**Changing the imputation method**\n\n"
    "Mice includes several imputation methods for imputing multilevel data:\n\n"
    "- `2l.norm`: Gibbs sampler for two-level normal outcomes with heterogeneous class "
    "variances\n"
    "- `2l.pan`: Homoscedastic two-level normal via the `pan` package\n"
    "- `2lonly.mean`: Class mean (or mode) imputation at level 2\n"
    "- `2lonly.norm`: Level-2 Bayesian normal regression (cluster aggregation)\n"
    "- `2lonly.pmm`: Level-2 predictive mean matching (cluster aggregation)\n"
    "- `2logreg`: Alias for `logreg` (R V05 uses `logreg` in `meth`; `#2logreg` is a predictor comment)\n\n"
    "The latter two methods aggregate level-1 variables at level 2, but in combination with "
    "`mice.impute.2l.pan`, allow switching regression imputation between level 1 and level 2 "
    "as described in Yucel (2008) or Gelman and Hill (2007, p. 541). For more information on "
    "these imputation methods see the help."
)

N21_2L_NORM = (
    "In the predictor matrix, `-2` denotes the class variable, a value `1` indicates a fixed "
    "effect and a value `2` indicates a random effect. However, the currently implemented "
    "algorithm does not handle predictors that are specified as fixed effects (type = `1`). "
    "When using `mice.impute.2l.norm()`, the current advice is to specify all predictors as "
    "random effects (type = `2`)."
)

N22_AFTER = (
    "The imputations generated with `2l.norm` are very similar to the ones obtained by `pmm` "
    "with `class` as a fixed effect. If we plot the first imputed dataset from `imp4` and "
    "`imp5` against the original (true) data we can see that the imputations are very similar. "
    "When studying the convergence we conclude that it may be wise to run additional "
    "iterations. Convergence is not apparent from this plot. After running another 10 "
    "iterations, convergence is more convincing."
)

N23_AFTER = (
    "Let us create the densityplot for `imp6` and compare it to the one for `imp4`. "
    "If we plot the first imputed dataset from both objects against the original (true) "
    "density, we can see that the imputations are very similar. When studying the convergence "
    "we conclude that it may be wise to run additional iterations. After running another "
    "10 iterations, convergence is more convincing."
)

N25_EVAL = (
    "Given what we know about the missingness, the imputed densities look very reasonable.\n\n"
    "Convergence has not yet been reached. More iterations are advisable."
)

N26_PMM = (
    "With `pmm`, the imputations are very similar and conform to the shape of the observed "
    "data.\n\n"
    "When looking at the convergence of `pmm`, more iterations are advisable:"
)

N26_REFERENCES = (
    "**References**\n\n"
    "Gelman, A., & Hill, J. (2006). *Data analysis using regression and multilevel/"
    "hierarchical models*. Cambridge University Press.\n\n"
    "Hox, J. J., Moerbeek, M., & van de Schoot, R. (2010). *Multilevel analysis: "
    "Techniques and applications*. Routledge.\n\n"
    "Yucel, R. M. (2008). Multiple imputation inference for multivariate multilevel "
    "continuous data with ignorable non-response. *Philosophical Transactions of the Royal "
    "Society of London A: Mathematical, Physical and Engineering Sciences*, 366(1874), "
    "2389-2403."
)

N26_CONCLUSION = (
    "**Conclusions**\n\n"
    'There are ways to ensure that imputations are not just "guesses of unobserved values". '
    "Imputations can be checked by using a standard of reasonability. We are able to check the "
    "differences between observed and imputed values, the differences between their "
    "distributions as well as the distribution of the completed data as a whole. If we do this, "
    "we can see whether imputations make sense in the context of the problem being studied.\n\n"
    "**- End of Vignette**"
)

N16_AFTER = "What do you think of the imputed values?"


def load_intro() -> str:
    data = json.loads(_PROSE.read_text(encoding="utf-8"))
    intro = data["intro"]
    intro = intro.replace(
        "This is the fifth vignette in a series of six.",
        "This is the fifth vignette in an eight-part series (see the index for the full path).",
    )
    ls_marker = "`ls()`"
    if ls_marker in intro:
        before, _, after = intro.partition(ls_marker)
        if "## [9]" in after:
            after = after.split("`", 1)[-1]  # drop R workspace listing block
            if after.startswith("##"):
                after = after.split("`", 1)[-1] if "`" in after else after
            # skip through closing backtick of listing if still present
            if after.lstrip().startswith("The dataset"):
                pass
            else:
                idx = after.find("The dataset")
                if idx >= 0:
                    after = after[idx:]
        intro = (
            before + "If you'd like to see what is inside the R workspace, run `ls()`. "
            "PyMICE loads the same datasets directly (`popNCR`, `popNCR2`, `popNCR3`, `popular`, …) "
            "via `lib.data` — no workspace dump is shown here.\n\n" + after.lstrip()
        )
    return intro


def load_step_title(num: int) -> str:
    return step_title("05", num)
