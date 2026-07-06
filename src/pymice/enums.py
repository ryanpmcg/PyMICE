"""Typed enums for imputation methods and block layout."""

from __future__ import annotations

from enum import Enum


class BlockPartition(str, Enum):
    """How variables are grouped into joint imputation blocks."""

    SCATTER = "scatter"
    COLLECT = "collect"
    VOID = "void"

    def __str__(self) -> str:
        return self.value


class ImputationMethod(str, Enum):
    """Registered univariate / multivariate imputation method names."""

    SKIP = ""
    PMM = "pmm"
    NORM = "norm"
    NORM_NOB = "norm.nob"
    NORM_BOOT = "norm.boot"
    NORM_PREDICT = "norm.predict"
    MEAN = "mean"
    SAMPLE = "sample"
    LOGREG = "logreg"
    POLYREG = "polyreg"
    POLR = "polr"
    MIDASTOUCH = "midastouch"
    CART = "cart"
    TWO_LEVEL_NORM = "2l.norm"
    TWO_LEVEL_PAN = "2l.pan"
    TWO_LEVEL_MEAN = "2lonly.mean"
    TWO_LEVEL_ONLY_NORM = "2lonly.norm"
    TWO_LEVEL_ONLY_PMM = "2lonly.pmm"
    TWO_LEVEL_LMER = "2l.lmer"
    TWO_LEVEL_BIN = "2l.bin"
    MICEMEAN = "micemean"
    QUADRATIC = "quadratic"
    LOGREG_BOOT = "logreg.boot"
    LDA = "lda"
    MNAR = "mnar"
    RI = "ri"
    JOMO = "jomoImpute"
    JOMO2CON = "jomo2con"
    JOMO2RAN = "jomo2ran"
    PAN = "panImpute"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def coerce(cls, value: str | ImputationMethod) -> str:
        if isinstance(value, cls):
            return value.value
        return str(value)
