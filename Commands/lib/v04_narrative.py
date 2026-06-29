"""Original prose from Vignettes/04_passive_post_processing/vignette.html."""

from __future__ import annotations

import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_PROSE = _ROOT / "Vignettes" / "04_passive_post_processing" / "vignette_prose.json"

AUTHORS = "Gerko Vink and Stef van Buuren"
SERIES_LABEL = "Vignette 4 of 6"
TITLE = "`mice`: Passive imputation and Post-processing"

PART_POST = "Post-processing of the imputations"

STEP_TITLES: dict[int, str] = {
    1: "Open `R` and load the packages `mice` and `lattice`.",
    2: (
        "Use passive imputation to impute the deterministic sleep relation in the "
        "`mammalsleep` data. Name the new multiply imputed dataset `pas.imp`."
    ),
    3: "Inspect the trace lines for `pas.imp`.",
    4: (
        "Post-process the values to constrain them between 1 and 25, use `norm` as the "
        "imputation method for `tv`."
    ),
    5: (
        "Compare the imputed values and histograms of `tv` for the solution obtained by "
        "`pmm` to the constrained solution (created with `norm`, constrained between 1 and 25)."
    ),
    6: (
        "Make a missing data indicator (name it `miss`) for `bmi` and check the relation of "
        "`bmi`, `wgt` and `hgt` for the boys in the imputed data. To do so, plot the imputed "
        "values against their respective calculated values."
    ),
    7: (
        "Use passive imputation to conserve the relation between imputed `bmi`, `wgt` and "
        "`hgt` by setting the imputation method for `bmi` to "
        "`meth[\"bmi\"]<- \"~ I(wgt / (hgt / 100)^2)\"`."
    ),
    8: (
        "Again, plot the imputed values of `bmi` versus the calculated values and check "
        "whether there is convergence for `bmi`."
    ),
    9: (
        "Solve the problem of circularity (if you did not already do so) and plot once again "
        "the imputed values of bmi versus the calculated values."
    ),
}

N1_AFTER = (
    "We choose seed value `123`. This is an arbitrary value; any value would be an equally good "
    "seed value. Fixing the random seed enables you (and others) to exactly replicate anything "
    "that involves random number generators. If you set the seed in your `R` instance to `123`, "
    "you will get the exact same results and plots as we present in this document."
)

N1_PASSIVE = (
    "**Passive Imputation**\n\n"
    "There is often a need for transformed, combined or recoded versions of the data. In the case "
    "of incomplete data, one could impute the original, and transform the completed original "
    "afterwards, or transform the incomplete original and impute the transformed version. If, "
    "however, both the original and the transformed version are needed within the imputation "
    "algorithm, neither of these approaches work: One cannot be sure that the transformation holds "
    "between the imputed values of the original and transformed versions. `mice` has a built-in "
    "approach, called *passive imputation*, to deal with situations as described above. The goal "
    "of passive imputation is to maintain the consistency among different transformations of the "
    "same data. As an example, consider the following deterministic function in the `boys` data "
    "\\[\\text{BMI} = \\frac{\\text{Weight (kg)}}{\\text{Height}^2 \\text{(m)}}\\] "
    "or the compositional relation in the mammalsleep data: \\[\\text{ts} = \\text{ps}+\\text{sws}\\]"
)

N2_AFTER = (
    "We used a custom predictor matrix and method vector to tailor our imputation approach to the "
    "passive imputation problem. We made sure to exclude `ts` as a predictor for the imputation of "
    "`sws` and `ps` to avoid circularity.\n\n"
    "We also gave the imputation algorithm 10 iterations to converge and fixed the seed to `123` "
    "for this `mice` instance. This means that even when people do not fix the overall `R` seed "
    "for a session, exact replication of results can be obtained by simply fixing the `seed` for "
    "the random number generator within `mice`. Naturally, the same input (data) is each time "
    "required to yield the same output (`mids`-object)."
)

N3_AFTER = (
    "We can see that the pathological nonconvergence we experienced before has been properly dealt "
    "with. The trace lines for the sleep variable look okay now and convergence can be inferred by "
    "studying the trace lines."
)

N3_POST = (
    "Remember that we imputed the `boys` data in the previous tutorial with `pmm` and with `norm`. "
    "One of the problems with the imputed values of `tv` with `norm` is that there are negative "
    "values among the imputations. Somehow we should be able to lay a constraint on the imputed "
    "values of `tv`.\n\n"
    "The `mice()` function has an argument called `post` that takes a vector of strings of `R` "
    "commands. These commands are parsed and evaluated after the univariate imputation function "
    "returns, and thus provides a way of post-processing the imputed values while using the "
    "processed version in the imputation algorithm. In other words; the post-processing allows us "
    "to manipulate the imputations for a particular variable that are generated within each "
    "iteration. Such manipulations directly affect the imputated values of that variable and the "
    "imputations for other variables. Naturally, such a procedure should be handled with care."
)

N4_AFTER = (
    "In this way the imputed values of `tv` are constrained (squeezed by function `squeeze()`) "
    "between 1 and 25."
)

N5_BEFORE_PMM = "First, we recreate the default `pmm` solution"
N5_AFTER_NORM = (
    "It is clear that the norm solution does not give us integer data as imputations. Next, we "
    "inspect and compare the density of the incomplete and imputed data for the constrained solution."
)
N5_AFTER_DENSITY = (
    "A nice way of plotting the histograms of both datasets simultaneously is by creating first "
    "the dataframe (here we named it `tvm`) that contains the data in one column and the imputation "
    "method in another column."
)
N5_AFTER_HIST = (
    "Is there still a difference in distribution between the two different imputation methods? "
    "Which imputations are more plausible do you think?"
)

N6_AFTER = (
    "With this plot we show that the relation between `hgt`, `wgt` and `bmi` is not preserved in "
    "the imputed values. In order to preserve this relation, we should use passive imputation."
)

N7_AFTER = (
    "Although the relation of `bmi` is preserved now in the imputations we get absurd imputations "
    "and on top of that we clearly see there are some problems with the convergence of `bmi`. The "
    "problem is that we have circularity in the imputations. We used passive imputation for `bmi` "
    "but `bmi` is also automatically used as predictor for `wgt` and `hgt`. This can be solved by "
    "adjusting the predictor matrix."
)

N8_BEFORE_XY = "To inspect the relation:"
N8_BEFORE_PLOT = "To study convergence for `bmi` alone:"

N9_BEFORE_PRED = "First, we remove `bmi` as a predictor for `hgt` and `wgt` to remove circularity."
N9_AFTER_PRED = (
    "and we run the `mice` algorithm again with the new predictor matrix (we still ‘borrow’ the "
    "imputation methods object `meth` from before)"
)
N9_BEFORE_XY = (
    "Second, we recreate the plots from **Assignment 8**. We start with the plot to inspect the "
    "relations in the observed and imputed data"
)
N9_BEFORE_TRACE = "and continue with the trace plot to study convergence"
N9_AFTER_OK = "All is well now!"

N9_CONCLUSION = (
    "**Conclusion**\n\n"
    "We have seen that the practical execution of multiple imputation and pooling is "
    "straightforward with the `R` package `mice`. The package is designed to allow you to assess "
    "and control the imputations themselves, the convergence of the algorithm and the distributions "
    "and multivariate relations of the observed and imputed data.\n\n"
    "It is important to ‘gain’ this control as a user. After all, we are imputing values and "
    "taking their uncertainty properly into account. Being also uncertain about the process that "
    "generated those values is therefor not a valid option."
)

N9_FUN = (
    "**For fun: what you shouldn’t do with passive imputation**\n\n"
    "Never set all relations fixed. You will remain with the starting values and waste your "
    "computer’s energy (and your own)."
)

N9_FUN_AFTER = (
    "We named the `mids`- object `imp.path`, because the nonconvergence is pathological in this "
    "example!\n\n"
    "**- End of Vignette**"
)


def load_intro() -> str:
    data = json.loads(_PROSE.read_text(encoding="utf-8"))
    return data["intro"]


def load_step_title(num: int) -> str:
    return STEP_TITLES[num]
