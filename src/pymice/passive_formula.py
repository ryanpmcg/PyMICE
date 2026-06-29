"""Passive imputation formula helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PassiveFormula:
    """Deterministic passive imputation specification."""

    expression: str

    def __str__(self) -> str:
        text = self.expression.strip()
        return text if text.startswith("~") else f"~ {text}"

    @classmethod
    def from_string(cls, text: str) -> PassiveFormula:
        return cls(expression=text.lstrip("~").strip() if text.lstrip().startswith("~") else text)
