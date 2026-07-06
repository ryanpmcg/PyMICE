"""Static help pages for datasets and API entry points (R ``help()`` analogue)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class HelpPage:
    """One help topic."""

    title: str
    kind: Literal["package", "dataset", "function"]
    description: str
    usage: str = ""
    details: str = ""
    variables: tuple[tuple[str, str], ...] = ()
    parameters: tuple[tuple[str, str], ...] = ()
    see_also: tuple[str, ...] = ()
    source: str = ""


PACKAGE_PAGE = HelpPage(
    title="pymice",
    kind="package",
    description=(
        "PyMICE implements Fully Conditional Specification (FCS) / MICE for incomplete "
        "multivariate data. The API mirrors R ``mice`` where that aids migration; call "
        "``help('topic')`` for datasets and functions."
    ),
    usage="import pymice\nhelp()  # or help('mice'), help('nhanes')",
    see_also=(
        "mice",
        "mice_df",
        "complete",
        "pool",
        "with_mids",
        "with_imputations",
        "parallel_mice",
        "md_pattern",
        "ampute",
        "load_nhanes",
        "nhanes",
        "boys",
        "mammalsleep",
    ),
)

PAGES: dict[str, HelpPage] = {
    "__package__": PACKAGE_PAGE,
    "pymice": PACKAGE_PAGE,
    "mice": HelpPage(
        title="mice",
        kind="function",
        description="Run MICE (Fully Conditional Specification) on incomplete data.",
        usage=(
            "from pymice import mice\n"
            "result = mice(data, m=5, maxit=10, seed=1)\n"
            "# or with explicit column metadata:\n"
            "result = mice(matrix, column_names=names, variable_specs=specs)"
        ),
        parameters=(
            ("data", "2-D array or column dict of incomplete values (NaN = missing)."),
            ("m", "Number of imputed datasets (parallel chains)."),
            ("maxit", "Gibbs iterations per imputation."),
            ("method", "Per-variable or per-block imputation method name(s)."),
            ("predictor_matrix", "0/1 matrix: which columns predict each target."),
            ("blocks", "Joint imputation blocks (e.g. collect / scatter)."),
            ("seed", "RNG seed for reproducibility."),
            ("where", "Boolean mask of cells that may be imputed."),
            ("post", "Post-processing hooks applied after each draw."),
            ("n_burn, n_iter", "MCMC burn-in / iterations for multilevel methods."),
        ),
        see_also=(
            "complete",
            "pool",
            "quickpred",
            "md_pattern",
            "with_mids",
            "unimplemented",
            "filter_mids",
        ),
        source="van Buuren & Groothuis-Oudshoorn (2011), JSS 45(3).",
    ),
    "filter_mids": HelpPage(
        title="filter_mids",
        kind="function",
        description=(
            "Subset imputations from a mids object (R ``filter()`` on mids). "
            "Uses **1-based** imputation indices like R."
        ),
        usage="from pymice import filter_mids\nsubset = filter_mids(imp, [1, 3, 5])",
        see_also=("ibind", "filter_imputations", "complete"),
    ),
    "unimplemented": HelpPage(
        title="unimplemented",
        kind="function",
        description=(
            "Some R ``mice`` methods and mids utilities are intentionally absent. "
            "Call ``unimplemented_imputation_methods()`` or ``unimplemented_features()`` "
            "for the current list. Using a listed method in ``mice()`` raises "
            "``NotImplementedError`` with guidance — never a silent fallback."
        ),
        usage=(
            "from pymice import unimplemented_imputation_methods, unimplemented_features\n"
            "print(unimplemented_imputation_methods())\n"
            "print(unimplemented_features())"
        ),
        see_also=("mice", "2l.norm", "jomoImpute", "as_mids"),
    ),
    "complete": HelpPage(
        title="complete",
        kind="function",
        description="Extract one or more completed datasets from a ``Mids`` object.",
        usage="from pymice import complete\nfilled = complete(result, draw=1)",
        parameters=(
            ("object", "``Mids`` result from ``mice()``."),
            ("draw", "Imputation index (1..m) or 'all' / 'long' / 'broad' layouts."),
        ),
        see_also=("mice", "with_mids", "pool"),
    ),
    "pool": HelpPage(
        title="pool",
        kind="function",
        description="Pool scalar estimates across repeated complete-data fits (Rubin's rules).",
        usage="from pymice import pool, with_mids\nfits = with_mids(result, formula='y ~ x')\npooled = pool(fits)",
        see_also=("with_mids", "summary_pool", "complete"),
    ),
    "with_mids": HelpPage(
        title="with_mids",
        kind="function",
        description="Fit a complete-data model on each imputation (R ``with()`` analogue).",
        usage="fits = with_mids(result, formula='bmi ~ chl')",
        see_also=("with_imputations", "pool", "lm", "mice"),
    ),
    "with_imputations": HelpPage(
        title="with_imputations",
        kind="function",
        description="Pythonic alias for ``with_mids`` with a formula-first keyword API.",
        usage="from pymice import with_imputations\nfits = with_imputations(result, formula='age ~ bmi')",
        see_also=("with_mids", "pool", "lm"),
    ),
    "mice_df": HelpPage(
        title="mice_df",
        kind="function",
        description="Run ``mice()`` on a pandas DataFrame (column names inferred from index).",
        usage="from pymice import mice_df\nresult = mice_df(df, m=5, maxit=10, seed=1)",
        parameters=(
            ("df", "pandas DataFrame with numeric columns (NaN = missing)."),
            ("**kwargs", "Forwarded to ``mice()`` (``m``, ``maxit``, ``method``, etc.)."),
        ),
        see_also=("mice", "ImputationFrame", "complete"),
    ),
    "parallel_mice": HelpPage(
        title="parallel_mice",
        kind="function",
        description="Run imputation chains in parallel (R ``futuremice`` workflow).",
        usage=(
            "from pymice import parallel_mice\n"
            "result = parallel_mice(data, m=10, n_jobs=4, parallelseed=123)"
        ),
        parameters=(
            ("m", "Number of imputations distributed across workers."),
            ("n_jobs", "Worker processes (``n.core`` alias)."),
            ("parallelseed", "Reproducibility seed stored on ``Mids.parallelseed``."),
        ),
        see_also=("merge_mids", "mice", "continue_imputation"),
    ),
    "merge_mids": HelpPage(
        title="merge_mids",
        kind="function",
        description="Combine single-chain ``Mids`` objects into one multiply imputed result.",
        usage="from pymice import merge_mids\nmerged = merge_mids([chain1, chain2, chain3])",
        see_also=("parallel_mice", "mice"),
    ),
    "continue_imputation": HelpPage(
        title="continue_imputation",
        kind="function",
        description="Warm-start additional Gibbs iterations from the last imputation draw.",
        usage="from pymice import continue_imputation\nextended = continue_imputation(result, max_iter=5)",
        see_also=("mice", "complete"),
    ),
    "load_nhanes": HelpPage(
        title="load_nhanes",
        kind="function",
        description="Load the bundled NHANES lipid subset as a numeric matrix.",
        usage="from pymice import load_nhanes\ndata, names = load_nhanes()",
        see_also=("nhanes", "mice", "md_pattern"),
    ),
    "md_pattern": HelpPage(
        title="md_pattern",
        kind="function",
        description="Tabulate missing-data patterns (R ``md.pattern()``).",
        usage=(
            "from pymice import md_pattern\n"
            "pat = md_pattern(data)\n"
            "md_pattern(data, plot=True)  # R-style grid"
        ),
        see_also=("mice", "nhanes", "boys"),
    ),
    "ampute": HelpPage(
        title="ampute",
        kind="function",
        description=(
            "Introduce missing values under MCAR, MAR, or MNAR mechanisms for simulation "
            "and sensitivity analysis."
        ),
        usage=(
            "from pymice import ampute\n"
            "result = ampute(data, prop=0.3, mech='MAR', seed=2016)\n"
            "amp = result.amp  # amputed data"
        ),
        parameters=(
            ("data", "Complete numeric array."),
            ("prop", "Target proportion of missing cells."),
            ("mech", "'MCAR', 'MAR', or 'MNAR'."),
            ("weights", "Column weights for MAR/MNAR sum-score mechanism."),
            ("patterns", "Binary pattern matrix (optional)."),
            ("bycases", "If True, delete rows; if False, delete cells per column."),
            ("seed", "RNG seed."),
        ),
        see_also=("mice", "md_pattern"),
        source="Schouten, Lugtig & Vink (2018); mice_ampute vignette.",
    ),
    "quickpred": HelpPage(
        title="quickpred",
        kind="function",
        description="Build a predictor matrix from pairwise associations (R ``quickpred()``).",
        usage="from pymice import quickpred\npred = quickpred(data, mincor=0.3, column_names=names)",
        see_also=("mice", "make_predictor_matrix"),
    ),
    "nhanes": HelpPage(
        title="nhanes",
        kind="dataset",
        description="Small subset of NHANES lipid data (Schafer, 1997, Table 6.14).",
        usage="from pymice import load_nhanes\ndata, names = load_nhanes()",
        variables=(
            ("age", "Age group (1–3)."),
            ("bmi", "Body mass index (kg/m²)."),
            ("hyp", "Hypertension (1=no, 2=yes)."),
            ("chl", "Total serum cholesterol (mg/dl)."),
        ),
        details="25 rows; used in vignettes 01–02 and 08.",
        see_also=("mice", "md_pattern", "nhanes2"),
        source="Schafer (1997); bundled in R mice package.",
    ),
    "nhanes2": HelpPage(
        title="nhanes2",
        kind="dataset",
        description="NHANES subset with factor-coded age and hypertension.",
        variables=(
            ("age", "Age band (1=20–39, 2=40–59, 3=60–99)."),
            ("bmi", "Body mass index."),
            ("hyp", "Hypertension (1=no, 2=yes)."),
            ("chl", "Cholesterol."),
        ),
        see_also=("nhanes", "mice", "logreg"),
    ),
    "boys": HelpPage(
        title="boys",
        kind="dataset",
        description="Longitudinal growth data for Dutch boys (Fredriks et al.).",
        usage="from pymice import load_boys\nboys, names = load_boys()",
        variables=(
            ("age", "Age (years)."),
            ("hgt", "Height (cm)."),
            ("wgt", "Weight (kg)."),
            ("bmi", "Body mass index."),
            ("hc", "Head circumference (cm)."),
            ("gen", "Genitalia development stage (Tanner)."),
            ("phb", "Pubic hair stage."),
            ("tv", "Testicular volume (ml)."),
            ("reg", "Geographic region."),
        ),
        details="748 rows; strong relation between missingness and `tv`.",
        see_also=("mice", "md_pattern", "mammalsleep"),
    ),
    "mammalsleep": HelpPage(
        title="mammalsleep",
        kind="dataset",
        description="Allison & Cicchetti (1976) sleep and ecology data for mammalian species.",
        usage="from pymice import load_mammalsleep\ndata, names = load_mammalsleep()",
        variables=(
            ("species", "Species name (factor; often excluded from imputation)."),
            ("bw", "Body weight (kg)."),
            ("brw", "Brain weight (g)."),
            ("sws", "Slow-wave sleep (hours)."),
            ("ps", "Paradoxical (REM) sleep."),
            ("ts", "Total sleep (= sws + ps; passive imputation target)."),
            ("mls", "Maximum life span."),
            ("gt", "Gestation time."),
            ("pi", "Predation index."),
            ("sei", "Sleep exposure index."),
            ("odi", "Overall danger index."),
        ),
        details="62 species; compositional relation ts = sws + ps.",
        see_also=("boys", "mice", "pool"),
        source="Allison & Cicchetti (1976).",
    ),
    "leiden": HelpPage(
        title="leiden",
        kind="dataset",
        description="Leiden 85-plus study subset (van Buuren, 2012 sensitivity vignette).",
        variables=(
            ("sexe", "Sex."),
            ("lftanam", "Age at examination."),
            ("rrsyst", "Systolic blood pressure."),
            ("rrdiast", "Diastolic blood pressure."),
            ("dwa", "Dead within follow-up (event indicator)."),
            ("survda", "Survival time (days)."),
            ("alb", "Albumin."),
            ("chol", "Cholesterol."),
            ("mmse", "Mini-mental state examination."),
            ("woon", "Living situation."),
        ),
        see_also=("mice", "ampute", "post_add"),
    ),
    "popncr": HelpPage(
        title="popNCR",
        kind="dataset",
        description="Popular teacher / pupil multilevel data (complete version).",
        variables=(
            ("pupil", "Pupil identifier."),
            ("class", "Class (cluster) identifier."),
            ("extrav", "Extraversion."),
            ("sex", "Sex."),
            ("texp", "Teacher experience."),
            ("popular", "Pupil popularity."),
            ("popteach", "Teacher popularity."),
        ),
        see_also=("popncr2", "popncr3", "2l.norm", "2l.pan", "jomoImpute"),
    ),
    "popncr2": HelpPage(
        title="popNCR2",
        kind="dataset",
        description="Popular teacher data with missing `popular` (vignette 05, steps 21–23).",
        see_also=("popncr", "2l.norm", "2l.pan"),
    ),
    "popncr3": HelpPage(
        title="popNCR3",
        kind="dataset",
        description="Multilevel data with multiple incomplete level-1 variables (vignette 05, step 24).",
        see_also=("popncr2", "logreg", "2lonly.mean"),
    ),
}

_ALIASES: dict[str, str] = {
    "with": "with_mids",
    "mdpattern": "md_pattern",
    "futuremice": "parallel_mice",
    "mids": "continue_imputation",
    "filter": "filter_mids",
    "gaps": "unimplemented",
}


def resolve_topic(name: str) -> str | None:
    """Normalize topic string to registry key."""
    key = name.strip().lstrip("?").lower().replace(".", "_")
    if key in PAGES:
        return key
    return _ALIASES.get(key)
