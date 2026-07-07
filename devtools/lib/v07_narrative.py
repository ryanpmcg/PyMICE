"""Original prose from reference/07_ampute/vignette.html."""

from __future__ import annotations

import json

from lib.paths import REFERENCE_DIR
from lib.vignette_catalog import step_title

_PROSE = REFERENCE_DIR / "07_ampute" / "vignette_prose.json"

AUTHORS = "Rianne Schouten"
SERIES_LABEL = "Vignette 7 of 8"
TITLE = "Generate missing values with ampute"

STEP_TITLES: dict[int, str] = {
    1: "Use the help function to read `ampute`'s documentation.",
    2: "Generate complete test data with `mvrnorm` and inspect with `summary()`.",
    3: "Introduce missing values with default `ampute()` settings.",
    4: "Inspect the `mads` object metadata with `names(result)`.",
    5: "Investigate the missing data pattern with `md.pattern()`.",
    6: "Visualize the missingness pattern heatmap.",
    7: "Compare amputed vs observed values with `bwplot()`.",
    8: "Inspect amputed vs observed correlations with `xyplot()`.",
    9: "Specify the proportion of incomplete cases (`prop`).",
    10: "Specify the proportion of missing cells (`bycases = FALSE`).",
    11: "Generate MAR and MNAR missingness with `mech`.",
}

N1_BEFORE = (
    "Use the help function to read `ampute`'s documentation. The function is available "
    "in multiple imputation package **mice**."
)

N2_BEFORE = (
    "The first argument `data` is an input argument for a complete dataset. In this tutorial, "
    "as in many simulation studies, we will randomly generate a dataset to be our complete "
    "dataset. Here, we will use function `mvrnorm` from R-package **MASS** to sample from a "
    "multivariate normal distribution."
)

N3_BEFORE = (
    "We can immediately generate missing values by calling `ampute`. The resulting object is "
    "of class `mads` and contains the default values that are used as arguments. It is "
    "important to know that the incomplete dataset is stored under object `amp` in class `mads`."
)

N4_BEFORE = (
    "Apart from the argument values and the incomplete dataset, the `mads` object contains the "
    "assigned subset for each data row (`cand`), the weighted sum scores (`scores`) and the "
    "original data (`data`)."
)

N5_BEFORE = (
    "We can quickly investigate the incomplete dataset with function `md.pattern`, where the "
    "resulting visualization shows the missing data in red and the observed data in blue. The "
    "first row always shows the complete cases, of which we have approximately 50%. Each "
    "subsequent row depicts a specific missing data pattern. By default, `ampute` generates "
    "missing values in each variable. Note that because `md.pattern` sorts the columns in "
    "increasing order of missing data proportion, the variables are displayed in a different "
    "order than in the dataset itself."
)

N6_BEFORE = (
    "The missingness pattern heatmap (`md.pattern(..., plot=TRUE)`) visualizes which cells "
    "are observed (blue) versus missing (red). PyMICE reproduces the pattern counts in the "
    "console table above; the lattice heatmap is reference-only in this walkthrough."
)

N7_BEFORE = (
    "Function `bwplot` allows for a comparison between amputed and non-amputed data. Note "
    "that the function uses as input the `mads` object and not the incomplete dataset."
)

N8_BEFORE = (
    "Similar inspections can be done using the function `xyplot`. The scatterplots show the "
    "correlation between the variable values and the weighted sum scores."
)

N9_BEFORE = (
    "The argument `prop` specifies the **proportion** of incomplete rows. As a default, the "
    "missingness proportion is 0.5. A proportion of 0.5 means that 50% of the data rows will "
    "have missing values. This is not the same as the proportion of missing cells, because "
    "incomplete cases will still have some observed values for some variables."
)

N10_BEFORE = (
    "To specify the proportion of missing cells, additional argument `bycases` should be set "
    "to `FALSE`. As the `testdata` contains 10000 × 3 = 30000 cells, a missing data "
    "proportion of 0.2 means that approximately 6000 cells will become missing."
)

N10_AFTER = (
    "In combination with the current set of missing data patterns, the resulting proportion "
    "of incomplete cases is returned by `result$prop`."
)

N11_BEFORE = (
    "Argument `mech` in function `ampute` is a string with either `MCAR`, `MAR` or `MNAR`. "
    "For MAR missingness, the information about the missing data is in the observed data; "
    "for MNAR missingness, the information about the missing data is missing itself."
)


def load_intro() -> str:
    data = json.loads(_PROSE.read_text(encoding="utf-8"))
    return data["intro"]


def load_step_title(num: int) -> str:
    return step_title("07", num)
