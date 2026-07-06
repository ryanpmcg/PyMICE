"""Original prose from reference/08_futuremice/vignette.html."""

from __future__ import annotations

import json

from lib.paths import REFERENCE_DIR
from lib.vignette_catalog import step_title

_PROSE = REFERENCE_DIR / "08_futuremice" / "vignette_prose.json"

AUTHORS = "Thom Benjamin Volker and Gerko Vink"
SERIES_LABEL = "Futuremice tutorial"
TITLE = "Wrapper function `futuremice`"

STEP_TITLES: dict[int, str] = {
    1: "Impute `nhanes` with `futuremice()` and verify the `mids` class.",
    2: "Inspect the multiply imputed data set.",
    3: "Check the number of imputations `m`.",
    4: "Change the imputation method to Bayesian linear regression (`method = 'norm'`).",
    5: "Reproduce pooled results with `set.seed(123)` outside `futuremice`.",
    6: "Reproduce pooled results with `parallelseed` inside `futuremice`.",
    7: "Use a drawn `parallelseed` for reproducibility when no global seed is set.",
    8: "Combine `ampute` and parallel imputation on simulated data.",
}

N1_BEFORE = (
    "We will now discuss the arguments of function `futuremice`. Easy imputation of an "
    "incomplete dataset (say, `nhanes`) can be performed with `futuremice` in the following way."
)

N1_AFTER = (
    "The function returns a `mids` object as created by `mice`. In fact, `futuremice` makes "
    "use of function `mice::ibind` to combine the `mids` objects returned by the different "
    "cores. PyMICE provides `futuremice()` / `parallel_mice()` with the same API, distributing "
    "imputations across worker processes via `ProcessPoolExecutor`."
)

N2_BEFORE = (
    "All other parts of the `mids` object are standard. Inspect the imputation metadata with "
    "`print(imp)`."
)

N3_BEFORE = (
    "With `n.core`, the number of cores (or CPUs) is given, and the number of imputations `m` "
    "is (about) equally distributed over the cores. As a default, `m = 5`, just as in a "
    "regular `mice` call. We can check this by evaluating the `m` that is shown in the `mids` "
    "object."
)

N4_BEFORE = (
    "Function `futuremice` is able to deal with the conventional `mice` arguments. In order to "
    "change the imputation method from its default (predictive mean matching) to, for example, "
    "Bayesian linear regression, the `method` argument can be adjusted."
)

N5_BEFORE = (
    "In simulation studies, it is often desired to set a seed to make the results reproducible. "
    "Similarly to `mice`, the seed value for `futuremice` can be defined outside the function. "
    "Hence users can specify the following code to obtain identical results."
)

N6_BEFORE = (
    "A user can also specify a seed within the `futuremice` call, by specifying the argument "
    "`parallelseed`. This seed is parsed to `withr::local_seed()`, such that the global "
    "environment is not affected by a different seed within the `futuremice` function."
)

N7_BEFORE = (
    "If no seed is specified by the user, a seed will be drawn randomly and returned in "
    "`imp$parallelseed`, such that the user can reproduce the obtained results even when no "
    "seed is specified."
)

N8_BEFORE = (
    "The original vignette also demonstrates timing benchmarks on simulated data (Figures 1–2). "
    "Those wall-clock comparisons are **R-only** and skipped here. As a closing example, we "
    "ampute a small multivariate dataset and impute it with the same PyMICE workflow."
)


def load_intro() -> str:
    data = json.loads(_PROSE.read_text(encoding="utf-8"))
    return data["intro"]


def load_step_title(num: int) -> str:
    return step_title("08", num)
