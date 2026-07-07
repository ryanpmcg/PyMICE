"""Compose numbered vignette sections (narrative + R / Python / output blocks)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from lib.r_style import compare_output, format_tutorial_step_md


@dataclass
class TutorialPart:
    """One executable block inside a numbered R vignette step."""

    r_code: str = ""
    python_code: str = ""
    narrative_before: str = ""
    narrative_after: str = ""
    run: Callable[[], str] | None = None
    r_expected: str = ""
    atol: float = 1e-3
    exact: bool = False
    skip: bool = False
    skip_reason: str = ""
    partial: bool = False
    partial_reason: str = ""
    output_lang: str = "text"
    plot_note: str = ""
    is_plot: bool = False


def _informational_partial(part: TutorialPart, *, match: bool) -> bool:
    """``partial=True`` steps with nothing to compare (or already matching)."""
    if not part.partial or not match:
        return False
    if part.partial_reason and any(
        phrase in part.partial_reason
        for phrase in (
            "no R console output",
            "no printed output",
            "no console output",
            "no R snapshot",
            "R snapshot has no",
            "Package load",
            "shows code only",
            "Seed argument demonstration",
            "Creates `",
            "object created",
            "imputation complete",
            "imputation — no",
            "Truncated R help",
            "PyMICE closing demo",
            "PyMICE reproducibility",
            "Mids object",
            "n.core",
            "workspace `ls()`",
        )
    ):
        return True
    return not part.r_expected.strip()


@dataclass
class SectionStats:
    n_match: int = 0
    n_mismatch: int = 0
    n_skip: int = 0
    n_partial: int = 0
    n_info: int = 0


def render_tutorial_section(parts: list[TutorialPart], stats: SectionStats | None = None) -> str:
    """Render narrative and code blocks for one numbered vignette section."""
    chunks: list[str] = []
    st = stats or SectionStats()

    for part in parts:
        if part.narrative_before.strip():
            chunks.append(part.narrative_before.strip())

        if part.skip:
            st.n_skip += 1
            block = format_tutorial_step_md(
                part.r_code,
                part.python_code,
                f"(not run — {part.skip_reason})",
                status="skip",
                note=part.skip_reason,
                output_lang=part.output_lang,
            )
        elif part.is_plot:
            st.n_partial += 1
            block = format_tutorial_step_md(
                part.r_code,
                part.python_code,
                "(plot below)",
                status="partial",
                note=part.plot_note or "Matplotlib equivalent of the R lattice plot.",
                output_lang=part.output_lang,
            )
        else:
            if part.run is None:
                raise ValueError("TutorialPart requires run= when not skipped or plot")
            desc = (
                part.python_code.strip().splitlines()[0]
                if part.python_code.strip()
                else part.r_code.strip().splitlines()[0]
            )
            print(f"      [part] {desc}...", flush=True)
            actual = part.run()
            print("      [part] done", flush=True)
            match, diff = (
                compare_output(part.r_expected, actual, atol=part.atol, exact=part.exact)
                if part.r_expected
                else (True, "")
            )
            if part.partial and _informational_partial(part, match=match):
                status = "info"
                st.n_info += 1
                note = part.partial_reason
            elif part.partial and not _informational_partial(part, match=match):
                status = "partial"
                st.n_partial += 1
                note = part.partial_reason
            elif match:
                status = "match"
                st.n_match += 1
                note = ""
            else:
                status = "mismatch"
                st.n_mismatch += 1
                note = "Output differs from R vignette — see diff hint below."
            block = format_tutorial_step_md(
                part.r_code,
                part.python_code,
                actual,
                r_expected=part.r_expected,
                status=status,
                note=note,
                output_lang=part.output_lang,
            )
            if not match and not part.partial and diff:
                block += f"\n\n**Diff hint:**\n```text\n{diff[:2000]}\n```"

        chunks.append(block)
        if part.narrative_after.strip():
            chunks.append(part.narrative_after.strip())

    return "\n\n".join(chunks)
