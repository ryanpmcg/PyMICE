"""PyMICE — Multivariate Imputation by Chained Equations (MICE / FCS)."""

from pymice.ampute import AmputeResult, ampute, run_ampute_chain
from pymice.analysis.glm import glm
from pymice.analysis.ols import lm
from pymice.analysis.survival import coxph, leiden_coxph
from pymice.complete import complete
from pymice.continue_mids import continue_imputation
from pymice.datasets import (
    data,
    load_boys,
    load_leiden,
    load_mammalsleep,
    load_nhanes,
    load_nhanes2,
    load_popncr,
    load_popncr2,
    load_popncr3,
)
from pymice.diagnostics import MdPatternResult, convergence, md_pattern
from pymice.engine import mice
from pymice.enums import BlockPartition, ImputationMethod
from pymice.help import help, help_topics
from pymice.imputation_frame import ImputationFrame
from pymice.imputation_setup import (
    check_blocks,
    make_block_predictor_matrix,
    make_blocks,
    make_method,
    make_predictor_matrix,
    make_visit_sequence,
    name_blocks,
)
from pymice.mids_ops import filter_mids
from pymice.pandas_api import mice_df
from pymice.parallel import (
    core_selection_message,
    default_n_core,
    distribute_imputations,
    merge_mids,
    parallel_mice,
)
from pymice.passive_formula import PassiveFormula
from pymice.plot_dispatch import bwplot, densityplot, fluxplot, plot, stripplot, xyplot
from pymice.pool import D1, D2, D3, anova, pool, pool_scalar, summary_pool
from pymice.postprocess import PostContext, post_add, post_squeeze, squeeze
from pymice.quickpred import quickpred
from pymice.r_api import futuremice, mice_mids, summary, with_
from pymice.r_gaps import (
    as_mids,
    cbind_mids,
    rbind_mids,
    unimplemented_features,
    unimplemented_imputation_methods,
)
from pymice.r_prerequisite import (
    RPrerequisiteStatus,
    check_r_prerequisites,
    ensure_r_prerequisites,
    install_r,
)
from pymice.rng import RngBackend, RSession, make_rng, r_rng_available, resolve_rng_backend_name
from pymice.types import (
    FitResult,
    ImputationFits,
    Mids,
    Mira,
    PoolResult,
    VariableKind,
    VariableSpec,
    filter_imputations,
    ibind,
)
from pymice.with_mids import with_imputations, with_mids

__all__ = [
    "D1",
    "D2",
    "D3",
    "AmputeResult",
    "BlockPartition",
    "FitResult",
    "ImputationFits",
    "ImputationFrame",
    "ImputationMethod",
    "MdPatternResult",
    "Mids",
    "Mira",
    "PassiveFormula",
    "PoolResult",
    "PostContext",
    "RPrerequisiteStatus",
    "RSession",
    "RngBackend",
    "VariableKind",
    "VariableSpec",
    "ampute",
    "anova",
    "as_mids",
    "bwplot",
    "cbind_mids",
    "check_blocks",
    "check_r_prerequisites",
    "complete",
    "continue_imputation",
    "convergence",
    "core_selection_message",
    "coxph",
    "data",
    "default_n_core",
    "densityplot",
    "distribute_imputations",
    "ensure_r_prerequisites",
    "filter_imputations",
    "filter_mids",
    "fluxplot",
    "futuremice",
    "glm",
    "help",
    "help_topics",
    "ibind",
    "install_r",
    "leiden_coxph",
    "lm",
    "load_boys",
    "load_leiden",
    "load_mammalsleep",
    "load_nhanes",
    "load_nhanes2",
    "load_popncr",
    "load_popncr2",
    "load_popncr3",
    "make_block_predictor_matrix",
    "make_blocks",
    "make_method",
    "make_predictor_matrix",
    "make_rng",
    "make_visit_sequence",
    "md_pattern",
    "merge_mids",
    "mice",
    "mice_df",
    "mice_mids",
    "name_blocks",
    "parallel_mice",
    "plot",
    "pool",
    "pool_scalar",
    "post_add",
    "post_squeeze",
    "quickpred",
    "r_rng_available",
    "rbind_mids",
    "resolve_rng_backend_name",
    "run_ampute_chain",
    "squeeze",
    "stripplot",
    "summary",
    "summary_pool",
    "unimplemented_features",
    "unimplemented_imputation_methods",
    "with_",
    "with_imputations",
    "with_mids",
    "xyplot",
]

__version__ = "0.1.0"
