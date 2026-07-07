#!/usr/bin/env python3
"""Verify displayed python_code strings in runners match intended operations."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

DEVTOOLS = Path(__file__).resolve().parent
RUNNERS = DEVTOOLS / "runners"

# Known display bugs: (file, snippet that must NOT appear, reason)
FORBIDDEN_SNIPPETS: list[tuple[str, str, str]] = [
    (
        "v02_convergence_pooling.py",
        "pred[:, names.index('age')] = 0",
        "Step 2 must zero hyp column, not age (R: pred[, 'hyp'] <- 0)",
    ),
]


def _extract_python_code_strings(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    codes: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "numbered_section":
            for kw in node.keywords:
                if kw.arg != "parts" or not isinstance(kw.value, ast.List):
                    continue
                for elt in kw.value.elts:
                    if not isinstance(elt, ast.Call):
                        continue
                    for pkw in elt.keywords:
                        if pkw.arg == "python_code" and isinstance(pkw.value, ast.Constant):
                            if isinstance(pkw.value.value, str):
                                codes.append(pkw.value.value)
    return codes


def audit_runners() -> list[str]:
    errors: list[str] = []
    for rel, forbidden, reason in FORBIDDEN_SNIPPETS:
        path = RUNNERS / rel
        if not path.exists():
            errors.append(f"Missing runner: {rel}")
            continue
        blob = path.read_text(encoding="utf-8")
        if forbidden in blob:
            errors.append(f"{rel}: {reason}")
    return errors


def main() -> int:
    errors = audit_runners()
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print("audit_code_display: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
