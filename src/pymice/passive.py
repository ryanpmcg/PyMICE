"""Passive imputation — derive variables from formulas during MICE."""

from __future__ import annotations

import ast
import operator
import re

import numpy as np
from numpy.typing import NDArray

from pymice.passive_formula import PassiveFormula

_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

_FUNCS = {
    "sqrt": np.sqrt,
    "log10": lambda x: np.log10(np.maximum(x, 1e-300)),
    "log": lambda x: np.log(np.maximum(x, 1e-300)),
    "abs": np.abs,
}


def is_passive(method: str | PassiveFormula) -> bool:
    """Return True when ``method`` is a passive formula (R ``is.passive``)."""
    if isinstance(method, PassiveFormula):
        return True
    return isinstance(method, str) and method.lstrip().startswith("~")


def _normalize_formula(formula: str) -> str:
    text = formula.strip()
    if text.startswith("~"):
        text = text[1:].strip()
    match = re.match(r"I\s*\((.*)\)\s*$", text, flags=re.DOTALL)
    if match:
        text = match.group(1).strip()
    # R uses ^ for exponentiation; Python ast expects **
    text = text.replace("^", "**")
    return text


def _eval_expr(node: ast.AST, env: dict[str, NDArray[np.float64]]) -> NDArray[np.float64]:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        first = next(iter(env.values()))
        return np.full(first.shape[0], float(node.value), dtype=np.float64)
    if isinstance(node, ast.Name):
        if node.id not in env:
            raise ValueError(f"unknown variable in passive formula: {node.id}")
        return env[node.id]
    if isinstance(node, ast.UnaryOp) and type(node.op) in _BINOPS:
        return _BINOPS[type(node.op)](_eval_expr(node.operand, env))
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        left = _eval_expr(node.left, env)
        right = _eval_expr(node.right, env)
        return _BINOPS[type(node.op)](left, right)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        fn = node.func.id
        if fn in _FUNCS and len(node.args) == 1 and not node.keywords:
            return _FUNCS[fn](_eval_expr(node.args[0], env))
    raise ValueError(f"unsupported expression in passive formula: {ast.dump(node)}")


def evaluate_passive(
    formula: str | PassiveFormula,
    data: NDArray[np.float64],
    column_names: list[str],
    wy: NDArray[np.bool_],
) -> NDArray[np.float64]:
    """Evaluate a passive formula on rows flagged by ``wy`` (R ``model.frame``)."""
    if not np.any(wy):
        return np.array([], dtype=np.float64)

    if isinstance(formula, PassiveFormula):
        formula = str(formula)
    expr = _normalize_formula(formula)
    tree = ast.parse(expr, mode="eval")
    env = {name: data[:, column_names.index(name)] for name in column_names}
    full = _eval_expr(tree.body, env)
    return np.asarray(full[wy], dtype=np.float64)
