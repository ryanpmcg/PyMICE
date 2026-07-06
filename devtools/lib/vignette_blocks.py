"""Parse R vignette snapshots and PyMICE runners into alignment manifests."""

from __future__ import annotations

import ast
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from lib.figure_map import REFERENCE_FIGURES
from lib.golden import _strip_r_console_markers
from lib.paths import DEVTOOLS_DIR, REFERENCE_DIR, REPO_ROOT, RUNNERS_DIR
from lib.vignette_catalog import METAS, STEP_TITLES, get_meta

ROOT = REPO_ROOT
VIGNETTES = REFERENCE_DIR
COMMANDS = DEVTOOLS_DIR
RUNNERS = RUNNERS_DIR

BLOCK_SEP = "# --- code block ---"

PLOT_MARKERS = (
    "plot(",
    "densityplot(",
    "stripplot(",
    "xyplot(",
    "bwplot(",
    "histogram(",
    "fluxplot(",
    "md.pattern(",
)


@dataclass
class RBlock:
    index: int
    type: str  # console | plot | setup
    r_code: str
    r_output: str = ""
    figure: str | None = None
    extra_figures: list[str] = field(default_factory=list)

    def normalized_code(self) -> str:
        return _normalize_r_code(self.r_code)


@dataclass
class ManifestStep:
    number: int
    title: str
    part: str = ""
    block_indices: list[int] = field(default_factory=list)


@dataclass
class VignetteManifest:
    vignette: str
    vignette_dir: str
    title: str
    runner: str
    blocks: list[RBlock]
    steps: list[ManifestStep]
    step_source: str = "runner_bootstrap"

    def to_dict(self) -> dict[str, Any]:
        return {
            "vignette": self.vignette,
            "vignette_dir": self.vignette_dir,
            "title": self.title,
            "runner": self.runner,
            "step_source": self.step_source,
            "blocks": [asdict(b) for b in self.blocks],
            "steps": [asdict(s) for s in self.steps],
        }


@dataclass
class RunnerPart:
    step: int
    part_index: int
    r_code: str
    r_expected: str | None
    r_expected_dynamic: bool
    python_code: str
    is_plot: bool
    skip: bool
    partial: bool
    plot_note: str
    narrative_before: str
    narrative_after: str


def _normalize_r_code(code: str) -> str:
    lines = [line.strip() for line in code.strip().splitlines() if line.strip()]
    return "\n".join(lines)


def _normalize_output(text: str) -> str:
    return _strip_r_console_markers(text)


def _md_pattern_plots(code: str) -> bool:
    """R ``md.pattern()`` defaults to ``plot=TRUE`` (table + graphic)."""
    normalized = _normalize_r_code(code).lower()
    if re.search(r"plot\s*=\s*(false|f)\b", normalized):
        return False
    return True


def _is_plot_code(code: str) -> bool:
    normalized = _normalize_r_code(code).lower()
    if not normalized:
        return False
    if "md.pattern(" in normalized:
        return _md_pattern_plots(code)
    first = normalized.splitlines()[0]
    return any(marker in first or marker in normalized for marker in PLOT_MARKERS)


def parse_extracted_r(text: str) -> list[RBlock]:
    """Split ``vignette_extracted.R`` into ordered code/output blocks."""
    chunks = text.split(BLOCK_SEP)
    blocks: list[RBlock] = []
    idx = 0

    header = chunks[0].strip() if chunks else ""
    if header:
        blocks.append(
            RBlock(
                index=idx,
                type="setup",
                r_code=header,
                r_output="",
            )
        )
        idx += 1

    for chunk in chunks[1:]:
        chunk = chunk.strip()
        if not chunk:
            continue
        code_lines: list[str] = []
        output_lines: list[str] = []
        phase = "code"
        for raw in chunk.splitlines():
            line = raw.rstrip()
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("##"):
                phase = "output"
                output_lines.append(stripped)
            elif phase == "code":
                code_lines.append(line)
            else:
                output_lines.append(stripped)

        r_code = "\n".join(code_lines).strip()
        r_output = _normalize_output("\n".join(output_lines))

        if not r_code and r_output and blocks:
            prev = blocks[-1]
            merged = _normalize_output(f"{prev.r_output}\n{r_output}".strip())
            blocks[-1] = RBlock(
                index=prev.index,
                type=prev.type,
                r_code=prev.r_code,
                r_output=merged,
                figure=prev.figure,
            )
            continue

        if not r_code:
            continue

        block_type = "plot" if _is_plot_code(r_code) else "console"
        blocks.append(
            RBlock(
                index=idx,
                type=block_type,
                r_code=r_code,
                r_output=r_output,
            )
        )
        idx += 1

    return blocks


def _ast_str(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                parts.append("{" + ast.unparse(value.value) + "}")
        return "".join(parts) if parts else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _ast_str(node.left)
        right = _ast_str(node.right)
        if left is not None and right is not None:
            return left + right
        return left if left is not None else right
    return None


def _ast_bool(node: ast.AST | None, default: bool = False) -> bool:
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    return default


def _kw_dict(call: ast.Call) -> dict[str, ast.AST]:
    out: dict[str, ast.AST] = {}
    for kw in call.keywords:
        if kw.arg:
            out[kw.arg] = kw.value
    return out


def parse_runner_parts(runner_path: Path) -> list[RunnerPart]:
    """Extract ``TutorialPart`` metadata from a vignette runner via AST."""
    tree = ast.parse(runner_path.read_text(encoding="utf-8"))
    parts: list[RunnerPart] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "b"
            and func.attr == "numbered_section"
        ):
            continue
        if len(node.args) < 3:
            continue
        step_node = node.args[0]
        if not isinstance(step_node, ast.Constant) or not isinstance(step_node.value, int):
            continue
        step = int(step_node.value)
        list_node = node.args[2]
        if not isinstance(list_node, ast.List):
            continue

        for part_index, elt in enumerate(list_node.elts):
            if not isinstance(elt, ast.Call):
                continue
            if not (isinstance(elt.func, ast.Name) and elt.func.id == "TutorialPart"):
                continue
            kw = _kw_dict(elt)
            r_code = _ast_str(kw.get("r_code")) or ""
            r_expected_node = kw.get("r_expected")
            r_expected = _ast_str(r_expected_node)
            parts.append(
                RunnerPart(
                    step=step,
                    part_index=part_index,
                    r_code=r_code,
                    r_expected=r_expected,
                    r_expected_dynamic=r_expected is None and r_expected_node is not None,
                    python_code=_ast_str(kw.get("python_code")) or "",
                    is_plot=_ast_bool(kw.get("is_plot")),
                    skip=_ast_bool(kw.get("skip")),
                    partial=_ast_bool(kw.get("partial")),
                    plot_note=_ast_str(kw.get("plot_note")) or "",
                    narrative_before=_ast_str(kw.get("narrative_before")) or "",
                    narrative_after=_ast_str(kw.get("narrative_after")) or "",
                )
            )

    return parts


def _match_block_for_code(blocks: list[RBlock], code: str, used: set[int]) -> RBlock | None:
    target = _normalize_r_code(code)
    if not target:
        return None
    for block in blocks:
        if block.index in used:
            continue
        if block.normalized_code() == target:
            used.add(block.index)
            return block
    # Prefix / containment fallback (R block may bundle extra lines)
    for block in blocks:
        if block.index in used:
            continue
        norm = block.normalized_code()
        if target in norm or norm in target:
            used.add(block.index)
            return block
    return None


def _attach_figures(vignette_num: str, steps: list[ManifestStep], blocks: list[RBlock]) -> None:
    fig_map = REFERENCE_FIGURES.get(vignette_num, {})
    for step in steps:
        figs = fig_map.get(step.number, [])
        if not figs:
            continue
        plot_blocks = [
            blocks[i] for i in step.block_indices if i < len(blocks) and blocks[i].type == "plot"
        ]
        for fig, block in zip(figs, plot_blocks, strict=False):
            block.figure = fig
        if len(figs) > len(plot_blocks) and plot_blocks:
            plot_blocks[-1].extra_figures = list(figs[len(plot_blocks) :])


def build_manifest(vignette_num: str) -> VignetteManifest:
    """Build manifest from extracted R, prose title, and runner step grouping."""
    meta = get_meta(vignette_num)
    vignette_dir = VIGNETTES / meta.vignette_dir
    extracted_path = vignette_dir / "vignette_extracted.R"
    prose_path = vignette_dir / "vignette_prose.json"
    runner_path = RUNNERS / f"{meta.slug}.py"

    blocks = parse_extracted_r(extracted_path.read_text(encoding="utf-8"))
    title = meta.reference_title
    if prose_path.is_file():
        prose = json.loads(prose_path.read_text(encoding="utf-8"))
        title = prose.get("title", title) or title

    runner_parts = parse_runner_parts(runner_path)
    used: set[int] = set()
    steps: list[ManifestStep] = []
    step_parts: dict[int, list[RunnerPart]] = {}
    for part in runner_parts:
        step_parts.setdefault(part.step, []).append(part)

    for step_num in sorted(step_parts):
        titles = STEP_TITLES.get(vignette_num, {})
        step_title = titles.get(step_num, f"Step {step_num}")
        indices: list[int] = []
        for rp in step_parts[step_num]:
            if rp.skip or not rp.r_code.strip():
                continue
            matched = _match_block_for_code(blocks, rp.r_code, used)
            if matched is not None:
                if rp.is_plot:
                    matched.type = "plot"
                indices.append(matched.index)
        steps.append(
            ManifestStep(
                number=step_num,
                title=step_title,
                block_indices=indices,
            )
        )

    _attach_figures(vignette_num, steps, blocks)

    return VignetteManifest(
        vignette=vignette_num,
        vignette_dir=meta.vignette_dir,
        title=title,
        runner=str(runner_path.relative_to(ROOT)),
        blocks=blocks,
        steps=steps,
    )


def write_manifest(manifest: VignetteManifest, path: Path | None = None) -> Path:
    out = path or (VIGNETTES / manifest.vignette_dir / "vignette_blocks.json")
    out.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")
    return out


def write_golden_outputs(manifest: VignetteManifest, path: Path | None = None) -> Path:
    """Optional golden store keyed by step and block index."""
    out = path or (VIGNETTES / manifest.vignette_dir / "golden_outputs.json")
    goldens: dict[str, dict[str, str]] = {}
    step_by_block = {idx: step.number for step in manifest.steps for idx in step.block_indices}
    for block in manifest.blocks:
        if not block.r_output:
            continue
        step_no = step_by_block.get(block.index, 0)
        key = f"{step_no}.{block.index}"
        goldens[key] = {
            "step": str(step_no),
            "block_index": str(block.index),
            "r_code": block.r_code,
            "r_output": block.r_output,
        }
    out.write_text(json.dumps(goldens, indent=2), encoding="utf-8")
    return out


def load_manifest(vignette_num: str) -> VignetteManifest:
    meta = get_meta(vignette_num)
    path = VIGNETTES / meta.vignette_dir / "vignette_blocks.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    blocks = [
        RBlock(
            **{
                **b,
                "extra_figures": b.get("extra_figures", []),
            }
        )
        for b in data["blocks"]
    ]
    steps = [ManifestStep(**s) for s in data["steps"]]
    return VignetteManifest(
        vignette=data["vignette"],
        vignette_dir=data["vignette_dir"],
        title=data.get("title", ""),
        runner=data.get("runner", ""),
        blocks=blocks,
        steps=steps,
        step_source=data.get("step_source", "unknown"),
    )


@dataclass
class AuditIssue:
    severity: str  # error | warning | info
    category: str
    step: int | None
    part_index: int | None
    message: str


def _parity_active_parts(parts: list[RunnerPart]) -> list[RunnerPart]:
    """Runner parts that map 1:1 to manifest R code blocks."""
    active: list[RunnerPart] = []
    for part in parts:
        if part.skip:
            continue
        # Plot-only display companions share a manifest block with a console part.
        if part.is_plot and not part.r_code.strip():
            continue
        active.append(part)
    return active


def _md_pattern_console_part(block: RBlock, part: RunnerPart) -> bool:
    """``md.pattern()`` is a plot block in R but also prints a console table."""
    if part.is_plot or block.type != "plot":
        return False
    if "md.pattern(" not in block.normalized_code().lower():
        return False
    return bool(block.r_output.strip())


def audit_vignette(vignette_num: str) -> list[AuditIssue]:
    """Compare runner TutorialParts against the block manifest."""
    manifest = load_manifest(vignette_num)
    runner_path = ROOT / manifest.runner
    parts = parse_runner_parts(runner_path)
    issues: list[AuditIssue] = []

    blocks_by_index = {b.index: b for b in manifest.blocks}
    manifest_parts: list[tuple[int, int, RBlock | None]] = []
    for step in manifest.steps:
        for bi, block_idx in enumerate(step.block_indices):
            manifest_parts.append((step.number, bi, blocks_by_index.get(block_idx)))

    # Per-step counts
    runner_by_step: dict[int, list[RunnerPart]] = {}
    for part in parts:
        runner_by_step.setdefault(part.step, []).append(part)

    manifest_by_step: dict[int, list[RBlock | None]] = {}
    for step in manifest.steps:
        manifest_by_step[step.number] = [blocks_by_index.get(i) for i in step.block_indices]

    for step_num in sorted(set(runner_by_step) | set(manifest_by_step)):
        r_parts = _parity_active_parts(runner_by_step.get(step_num, []))
        m_blocks = manifest_by_step.get(step_num, [])
        if len(r_parts) != len(m_blocks):
            issues.append(
                AuditIssue(
                    severity="error",
                    category="count_mismatch",
                    step=step_num,
                    part_index=None,
                    message=(
                        f"step {step_num}: runner has {len(r_parts)} active parts, "
                        f"manifest has {len(m_blocks)} blocks"
                    ),
                )
            )

    used_blocks: set[int] = set()
    for part in parts:
        if part.skip:
            issues.append(
                AuditIssue(
                    severity="info",
                    category="skipped",
                    step=part.step,
                    part_index=part.part_index,
                    message="runner part marked skip=True",
                )
            )
            continue

        block = _match_block_for_code(manifest.blocks, part.r_code, used_blocks)
        if block is None and part.r_code.strip():
            issues.append(
                AuditIssue(
                    severity="error",
                    category="missing_manifest_block",
                    step=part.step,
                    part_index=part.part_index,
                    message=f"no manifest block matches r_code:\n{part.r_code[:200]}",
                )
            )
            continue

        if block is None:
            continue

        norm_runner = _normalize_r_code(part.r_code)
        norm_block = block.normalized_code()
        if (
            norm_runner != norm_block
            and norm_runner not in norm_block
            and norm_block not in norm_runner
        ):
            issues.append(
                AuditIssue(
                    severity="warning",
                    category="r_code_drift",
                    step=part.step,
                    part_index=part.part_index,
                    message="runner r_code differs from manifest block text",
                )
            )

        if part.is_plot or block.type == "plot":
            md_console = _md_pattern_console_part(block, part)
            if not part.is_plot and not md_console:
                issues.append(
                    AuditIssue(
                        severity="warning",
                        category="plot_flag",
                        step=part.step,
                        part_index=part.part_index,
                        message="manifest block is plot but runner is_plot=False",
                    )
                )
            if part.r_expected and not part.r_expected_dynamic:
                issues.append(
                    AuditIssue(
                        severity="error",
                        category="plot_r_expected",
                        step=part.step,
                        part_index=part.part_index,
                        message="plot step has non-empty static r_expected (should be empty)",
                    )
                )
        elif part.r_expected_dynamic:
            issues.append(
                AuditIssue(
                    severity="info",
                    category="dynamic_golden",
                    step=part.step,
                    part_index=part.part_index,
                    message="r_expected is a variable reference — static audit skipped",
                )
            )
        elif part.r_expected and block.r_output:
            if _normalize_output(part.r_expected) != _normalize_output(block.r_output):
                issues.append(
                    AuditIssue(
                        severity="error",
                        category="r_expected_mismatch",
                        step=part.step,
                        part_index=part.part_index,
                        message="runner r_expected does not match manifest r_output",
                    )
                )
        elif part.r_expected and not block.r_output:
            issues.append(
                AuditIssue(
                    severity="warning",
                    category="missing_r_output",
                    step=part.step,
                    part_index=part.part_index,
                    message="runner expects output but manifest block has empty r_output",
                )
            )

        if not part.python_code.strip():
            issues.append(
                AuditIssue(
                    severity="warning",
                    category="empty_python_code",
                    step=part.step,
                    part_index=part.part_index,
                    message="python_code is empty",
                )
            )

    return issues


def format_audit_report(vignette_num: str, issues: list[AuditIssue]) -> str:
    meta = get_meta(vignette_num)
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]

    lines = [
        f"# Vignette alignment audit — V{vignette_num} ({meta.short_title})",
        "",
        f"Runner: `{METAS[vignette_num].slug}.py`",
        f"Manifest: `reference/{meta.vignette_dir}/vignette_blocks.json`",
        "",
        "## Summary",
        "",
        f"- **Errors:** {len(errors)}",
        f"- **Warnings:** {len(warnings)}",
        f"- **Info:** {len(infos)}",
        "",
    ]

    if not issues:
        lines.append("No structural alignment issues detected.")
        return "\n".join(lines)

    for label, group in ("Errors", errors), ("Warnings", warnings), ("Info", infos):
        if not group:
            continue
        lines.append(f"## {label}")
        lines.append("")
        for issue in group:
            loc = ""
            if issue.step is not None:
                loc = f"step {issue.step}"
                if issue.part_index is not None:
                    loc += f", part {issue.part_index}"
            lines.append(f"- **[{issue.category}]** {loc}: {issue.message}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
