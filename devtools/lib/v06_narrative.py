"""Original prose from reference/06_sensitivity_analysis/vignette.html."""

from __future__ import annotations

import json

from lib.paths import REFERENCE_DIR
from lib.vignette_catalog import step_title

_PROSE = REFERENCE_DIR / "06_sensitivity_analysis" / "vignette_prose.json"

AUTHORS = "Gerko Vink and Stef van Buuren"
SERIES_LABEL = "Vignette 6 of 8"
TITLE = "`mice`: An approach to sensitivity analysis"

STEP_TITLES: dict[int, str] = {
    1: "Open `R` and load the packages `mice`, `lattice` and `survival`.",
    2: "The leiden data set.",
    3: "Perform a dry run (using `maxit = 0`) in `mice`. List the number of missing values per variable.",
    4: (
        "Study the missing data pattern in more detail using `md.pattern()` and `fluxplot()`. "
        "The interest here focusses on imputing systolic blood pressure (`rrsyst`) and diastolic "
        "blood pressure (`rrdiast`)."
    ),
    5: (
        "The cases with and without blood pressure observed have very different survival rates. "
        "Show this."
    ),
    6: (
        "Create a δ vector that represent the following adjustment values for mmHg: 0 for MAR, "
        "and -5, -10, -15, and -20 for MNAR."
    ),
    7: (
        "Impute the leiden data using the delta adjustment technique. We only have to deduct from "
        "`rrsyst`, because `rrdiast` will adapt to the changed `rrsyst` when it is imputed using "
        "`rrsyst` as predictor. Store the five imputed scenarios (adjustment) in a list called "
        "`imp.all`."
    ),
    8: (
        "Inspect the imputations. Compare the imputations for blood pressure under the most "
        "extreme scenarios with a box-and-whiskers plot. Is this as expected?"
    ),
    9: "Use the density plot for another inspection.",
    10: (
        "Also create a scatter plot of `rrsyst` and `rrdiast` by imputation number and missingness."
    ),
    11: (
        "Create five fit objects that run the expression `cda` on the five imputed adjustment "
        "scenarios. Use function with()."
    ),
    12: "Pool the results for each of the five scenarios.",
    13: (
        "Perform sensitivity analysis analysis on the mammalsleep dataset by adding and "
        "subtracting some amount from the imputed values for sws. Use "
        "`delta <- c(8, 6, 4, 2, 0, -2, -4, -6, -8)` and investigating the influence on the "
        "following regression model:"
    ),
}

N1_AFTER = "We choose seed value `123` for reproducibility in the PyMICE walkthrough below."

N2_AFTER = (
    "There are 121 missings (`NA`'s) for `rrsyst`, 126 missings for `rrdiast`, 229 missings "
    "for `alb`, 232 missings for `chol` and 85 missing values for `mmse`."
)

N4_AFTER_FLUX = (
    "Variables with higher outflux are (potentially) the more powerful predictors. Variables with "
    "higher influx depend stronger on the imputation model. When points are relatively close to "
    "the diagonal, it indicates that influx and outflux are balanced.\n\n"
    "The variables in the upper left corner have the more complete information, so the number of "
    "missing data problems for this group is relatively small. The variables in the middle have "
    "an outflux between 0.5 and 0.8, which is small. Missing data problems are thus more "
    "severe, but potentially this group could also contain important variables. The lower (bottom) "
    "variables have an outflux with 0.5 or lower, so their predictive power is limited. Also, "
    "this group has a higher influx, and, thus, depend more highly on the imputation model."
)

N4_AFTER_MDP = (
    "In the next steps we are going to impute `rrsyst` and `rrdiast` under two scenarios: MAR and "
    "MNAR. We will use the delta adjustment technique described in paragraph 7.2.3 in "
    "Van Buuren (2012)"
)

N5_AFTER = (
    "In the next steps we are going to impute `rrsyst` and `rrdiast` under two scenarios: MAR "
    "and MNAR. We will use the delta adjustment technique described in paragraph 7.2.3 in "
    "Van Buuren (2012)"
)

N6_AFTER = (
    "The recipe for creating MNAR imputations for δ ≠ 0 uses the post-processing facility of "
    "`mice`. This allows to change the imputations on the fly by deducting a value of δ from "
    "the values just imputed."
)

N8_AFTER = (
    "We can clearly see that the adjustment has an effect on the imputations for `rrsyst` and, "
    "thus, on those for `rrdiast`."
)

N9_AFTER = (
    "We can once more clearly see that the adjustment has an effect on the imputations for "
    "`rrsyst` and, thus, on those for `rrdiast`."
)

N10_AFTER = (
    "The scatter plot comparison between `rrsyst` and `rrdiast` shows us that the adjustment has "
    "an effect on the imputations and that the imputations are lower for the situation where "
    "δ = -20.\n\n"
    "We are now going to perform a complete-data analysis. This involves several steps:\n\n"
    "In order to automate this step we should create an expression object that performs these "
    "steps for us. The following object does so:\n\n"
    "`cda <- expression(sbpgp <- cut(rrsyst, ...), coxph(...))`\n\n"
    "See Van Buuren (2012, pp.186) for more information."
)

N12_AFTER = (
    "All in all, it seems that even big changes to the imputations (e.g. deducting 20 mmHg) has "
    "little influence on the results. This suggests that the results are stable relatively to "
    "this type of MNAR-mechanism."
)

N13_LM = "`lm(sws ~ log10(bw) + odi)`"

N13_AFTER = (
    "Sensitivity analysis is an important tool for investigating the plausibility of the MAR "
    "assumption. We again use the δ-adjustment technique described in Van Buuren (2012, p. 185) "
    "as an informal, simple and direct method to create imputations under nonignorable models.\n\n"
    "**Conclusion**\n\n"
    "We have seen that we can create multiple imputations in multivariate missing data problems "
    "that imitate deviations from MAR. The analysis used the `post` argument of the `mice()` "
    "function as a hook to alter the imputations just after they have been created by a univariate "
    "imputation function. The diagnostics shows that the trick works. The relative mortality "
    "estimates are however robust to this type of alteration.\n\n"
    "**- End of Vignette**"
)


def load_intro() -> str:
    data = json.loads(_PROSE.read_text(encoding="utf-8"))
    return data["intro"]


def load_step_title(num: int) -> str:
    return step_title("06", num)
