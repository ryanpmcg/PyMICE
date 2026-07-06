"""Central metadata for PyMICE vignette reports (V1–V8)."""

from __future__ import annotations

from dataclasses import dataclass

COMPARISON_DISCLAIMER = (
    "This page walks through PyMICE equivalents of the numbered exercises in the "
    "reference vignette below. Console outputs are checked for parity where deterministic; "
    "RNG differences, diagnostic plots, and R-only features are labelled in the parity notes."
)


@dataclass(frozen=True)
class VignetteMeta:
    number: str
    slug: str
    short_title: str
    reference_title: str
    reference_author: str
    source_url: str
    vignette_dir: str


METAS: dict[str, VignetteMeta] = {
    "01": VignetteMeta(
        "01",
        "v01_ad_hoc_mice",
        "Ad Hoc MICE",
        "Ad hoc methods and mice",
        "Gerko Vink and Stef van Buuren",
        "https://www.gerkovink.com/micereference/Ad_hoc_and_mice/Ad_hoc_methods.html",
        "01_ad_hoc_and_mice",
    ),
    "02": VignetteMeta(
        "02",
        "v02_convergence_pooling",
        "Convergence Pooling",
        "Algorithmic convergence and inference pooling",
        "Gerko Vink and Stef van Buuren",
        "https://www.gerkovink.com/micereference/Convergence_pooling/Convergence_and_pooling.html",
        "02_convergence_and_pooling",
    ),
    "03": VignetteMeta(
        "03",
        "v03_missingness",
        "Missingness Models",
        "The imputation and nonresponse models",
        "Gerko Vink and Stef van Buuren",
        "https://www.gerkovink.com/micereference/Missingness_inspection/Missingness_inspection.html",
        "03_missingness_inspection",
    ),
    "04": VignetteMeta(
        "04",
        "v04_passive",
        "Passive Imputation",
        "Passive imputation and Post-processing",
        "Gerko Vink and Stef van Buuren",
        "https://www.gerkovink.com/micereference/Passive_Post_processing/Passive_imputation_post_processing.html",
        "04_passive_post_processing",
    ),
    "05": VignetteMeta(
        "05",
        "v05_multilevel",
        "Multilevel Data",
        "Imputing multi-level data",
        "Gerko Vink and Stef van Buuren",
        "https://www.gerkovink.com/micereference/Multi_level/Multi_level_data.html",
        "05_multilevel_data",
    ),
    "06": VignetteMeta(
        "06",
        "v06_sensitivity",
        "Sensitivity Analysis",
        "An approach to sensitivity analysis",
        "Gerko Vink and Stef van Buuren",
        "https://www.gerkovink.com/micereference/Sensitivity_analysis/Sensitivity_analysis.html",
        "06_sensitivity_analysis",
    ),
    "07": VignetteMeta(
        "07",
        "v07_ampute",
        "Ampute Simulation",
        "Generate missing values with ampute",
        "Rianne Schouten",
        "https://rianneschouten.github.io/mice_ampute/vignette/ampute.html",
        "07_ampute",
    ),
    "08": VignetteMeta(
        "08",
        "v08_futuremice",
        "Parallel MICE",
        "Wrapper function futuremice",
        "Thom Benjamin Volker and Gerko Vink",
        "https://www.gerkovink.com/micereference/futuremice/Vignette_futuremice.html",
        "08_futuremice",
    ),
}

# User-friendly step headings (numbering matches R vignettes).
STEP_TITLES: dict[str, dict[int, str]] = {
    "01": {
        1: "Load packages",
        2: "Inspect incomplete data",
        3: "Summarize variables",
        4: "Missing data pattern",
        5: "Regression on incomplete data",
        6: "Mean imputation",
        7: "Explore mean-imputed data",
        8: "Regression imputation",
        9: "Inspect regression imputation",
        10: "Stochastic regression imputation",
        11: "Inspect stochastic imputation",
        12: "Reproducible stochastic imputation",
        13: "Default MICE imputation",
        14: "Extract completed data",
    },
    "02": {
        1: "Vary number of imputations",
        2: "Edit predictor matrix",
        3: "Convergence trace plot",
        4: "Change imputation method",
        5: "Extended iteration trace",
        6: "Stripplot diagnostics",
        7: "Pooled regression fit",
        8: "Pool multiply imputed model",
    },
    "03": {
        1: "Load packages and seed",
        2: "Inspect boys dataset",
        3: "Dataset size and missingness",
        4: "Missing data patterns",
        5: "Patterns with missing gen",
        6: "Histogram by missing gen",
        7: "Default MICE imputation",
        8: "Compare imputed means",
        9: "Inspect mammalsleep data",
        10: "Impute mammalsleep with PMM",
        11: "Regression on mammalsleep",
        12: "Pool mammalsleep model",
        13: "Drop species column",
        14: "Re-impute without species",
        15: "Trace plot for impnew",
    },
    "04": {
        1: "Dry run predictor matrix",
        2: "Passive imputation formula",
        3: "Passive convergence trace",
        4: "PMM versus norm post",
        5: "Density comparison",
        6: "XY plot default PMM",
        7: "Passive BMI from weight and height",
        8: "Circular passive imputation",
        9: "Fixed passive imputation",
    },
    "05": {
        1: "Load packages and seed",
        2: "Inspect popNCR data",
        3: "Missing data patterns",
        4: "popular missingness vs popteach",
        5: "Other missingness vs popteach",
        6: "popteach missingness vs popular",
        7: "ICC for incomplete variables",
        8: "norm imputation imp1 (no class)",
        9: "Compare imputed vs incomplete means",
        10: "ICC comparison imp1",
        11: "norm imputation imp2 (with class)",
        12: "ICC comparison imp2 (normclass)",
        13: "Convergence trace imp2",
        14: "Extended trace imp3",
        15: "Density plots imp2",
        16: "First 15 imputed rows",
        17: "PMM imputation imp4",
        18: "Density plots imp4",
        19: "ICC imp4 (deferred)",
        20: "Full ICC comparison incl. orig",
        21: "2l.norm on popNCR2",
        22: "Inspect imp5 convergence",
        23: "2l.pan on popNCR2",
        24: "Mixed 2l setup on popNCR3",
        25: "Evaluate imp7",
        26: "PMM on popNCR3",
    },
    "06": {
        1: "Load packages",
        2: "Inspect leiden data",
        3: "Dry run missing counts",
        4: "Pattern and flux plots",
        5: "Kaplan–Meier by missingness",
        6: "Delta adjustment vector",
        7: "Delta-adjusted imputation",
        8: "Boxplot blood pressure",
        9: "Density blood pressure",
        10: "Scatter blood pressure",
        11: "Survival models per scenario",
        12: "Pool survival models",
        13: "Mammalsleep sensitivity",
    },
    "07": {
        1: "Read ampute documentation",
        2: "Generate complete data",
        3: "Default amputation",
        4: "Inspect mads metadata",
        5: "Missing data pattern",
        6: "Pattern heatmap",
        7: "Amputed boxplots",
        8: "Amputed scatterplots",
        9: "Proportion of incomplete cases",
        10: "Proportion of missing cells",
        11: "MAR and MNAR mechanisms",
    },
    "08": {
        1: "Default futuremice run",
        2: "Inspect mids object",
        3: "Number of imputations",
        4: "Change imputation method",
        5: "Global seed reproducibility",
        6: "Parallelseed reproducibility",
        7: "Drawn parallelseed",
        8: "Ampute then impute",
    },
}


def get_meta(number: str) -> VignetteMeta:
    key = number.lstrip("0") if number.isdigit() else number
    key = key.zfill(2) if len(key) == 1 else number
    if number in METAS:
        return METAS[number]
    if key in METAS:
        return METAS[key]
    raise KeyError(f"Unknown vignette number: {number}")


def all_metas_ordered() -> list[VignetteMeta]:
    return [METAS[f"{i:02d}"] for i in range(1, 9)]


def step_title(number: str, step: int) -> str:
    meta = get_meta(number)
    titles = STEP_TITLES.get(meta.number, {})
    if step not in titles:
        raise KeyError(f"No step title for vignette {meta.number} step {step}")
    return titles[step]


def nav_label(meta: VignetteMeta) -> str:
    n = int(meta.number)
    return f"V{n}: {meta.short_title}"
