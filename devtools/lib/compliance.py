"""Build vignette reports with R parity checks."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from lib.figure_map import reference_images_for_step
from lib.r_style import compare_output, format_step_md, format_tutorial_step_md
from lib.report import Section, VignetteReport
from lib.tutorial_section import SectionStats, TutorialPart, render_tutorial_section
from lib.vignette_catalog import VignetteMeta, get_meta


@dataclass
class VignetteBuilder:
    number: str
    slug: str
    title: str
    source_url: str
    short_title: str = ""
    reference_title: str = ""
    reference_author: str = ""
    sections: list[Section] = field(default_factory=list)
    image_paths: dict[str, list[Path]] = field(default_factory=dict)
    n_match: int = 0
    n_mismatch: int = 0
    n_skip: int = 0
    n_partial: int = 0
    disclaimer_md: str = ""
    parity_overview_md: str = ""
    intro_md: str = ""
    authors: str = ""
    series_label: str = ""

    @classmethod
    def from_meta(cls, meta: VignetteMeta) -> VignetteBuilder:
        return cls(
            number=meta.number,
            slug=meta.slug,
            title=meta.short_title,
            short_title=meta.short_title,
            reference_title=meta.reference_title,
            reference_author=meta.reference_author,
            source_url=meta.source_url,
        )

    def set_intro(self, text: str, *, authors: str = "", series_label: str = "") -> None:
        self.intro_md = text
        self.authors = authors
        self.series_label = series_label

    def set_disclaimer(self, text: str) -> None:
        """Preamble disclaimer (rendered after title, before exercises)."""
        self.disclaimer_md = text

    def set_parity_overview(self, text: str) -> None:
        """Expected match / RNG / not-implemented overview for this vignette."""
        self.parity_overview_md = text

    def step(
        self,
        exercise: str,
        r_code: str,
        r_expected: str,
        run: Callable[[], str] | None = None,
        *,
        atol: float = 1e-3,
        exact: bool = False,
        skip: bool = False,
        skip_reason: str = "",
        partial: bool = False,
        partial_reason: str = "",
        images: list[Path] | None = None,
    ) -> None:
        if skip:
            self.n_skip += 1
            body = format_step_md(
                exercise,
                r_code,
                r_expected,
                f"(not run — {skip_reason})",
                status="skip",
                note=skip_reason,
            )
            self.sections.append(Section(exercise, body, image_paths=images or []))
            return

        if run is None:
            raise ValueError(f"step '{exercise}' requires run= when not skipped")

        print(f"    [step] {exercise}...", flush=True)
        actual = run()
        print(f"    [step] {exercise}... done", flush=True)
        match, diff = compare_output(r_expected, actual, atol=atol, exact=exact)
        if partial:
            status = "partial"
            self.n_partial += 1
            note = partial_reason
        elif match:
            status = "match"
            self.n_match += 1
            note = ""
        else:
            status = "mismatch"
            self.n_mismatch += 1
            note = "Outputs differ — see blocks below."

        body = format_step_md(exercise, r_code, r_expected, actual, status=status, note=note)
        if not match and not partial and diff:
            body += f"\n\n**Diff hint:**\n```text\n{diff[:2000]}\n```"
        self.sections.append(Section(exercise, body, image_paths=images or []))

    def plot_step(
        self,
        exercise: str,
        r_code: str,
        description: str,
        images: list[Path],
        *,
        note: str = "Python equivalent (matplotlib); content matches R diagnostic.",
    ) -> None:
        """Record a plot-only step without numeric R comparison."""
        self.n_partial += 1
        body = "\n".join(
            [
                "**Compliance:** ⚠️ PARTIAL (plot)",
                f"**R code:** `{r_code}`",
                f"**Note:** {note}",
                "",
                description,
            ]
        )
        self.sections.append(Section(exercise, body, image_paths=images))

    def tutorial_step(
        self,
        exercise: str,
        r_code: str,
        python_code: str,
        run: Callable[[], str] | None = None,
        *,
        r_expected: str = "",
        atol: float = 1e-3,
        exact: bool = False,
        skip: bool = False,
        skip_reason: str = "",
        partial: bool = False,
        partial_reason: str = "",
        images: list[Path] | None = None,
        output_lang: str = "text",
    ) -> None:
        """R vignette layout: R code → Python code → formatted output."""
        if skip:
            self.n_skip += 1
            body = format_tutorial_step_md(
                r_code,
                python_code,
                f"(not run — {skip_reason})",
                status="skip",
                note=skip_reason,
                output_lang=output_lang,
            )
            self.sections.append(Section(exercise, body, image_paths=images or []))
            return

        if run is None:
            raise ValueError(f"tutorial_step '{exercise}' requires run= when not skipped")

        print(f"    [tutorial_step] {exercise}...", flush=True)
        actual = run()
        print(f"    [tutorial_step] {exercise}... done", flush=True)
        match, diff = (
            compare_output(r_expected, actual, atol=atol, exact=exact) if r_expected else (True, "")
        )
        if partial:
            status = "partial"
            self.n_partial += 1
            note = partial_reason
        elif match:
            status = "match"
            self.n_match += 1
            note = ""
        else:
            status = "mismatch"
            self.n_mismatch += 1
            note = "Output differs from R vignette — see diff hint below."

        body = format_tutorial_step_md(
            r_code,
            python_code,
            actual,
            r_expected=r_expected,
            status=status,
            note=note,
            output_lang=output_lang,
        )
        if not match and not partial and diff:
            body += f"\n\n**Diff hint:**\n```text\n{diff[:2000]}\n```"
        self.sections.append(Section(exercise, body, image_paths=images or []))

    def _merge_stats(self, stats: SectionStats) -> None:
        self.n_match += stats.n_match
        self.n_mismatch += stats.n_mismatch
        self.n_skip += stats.n_skip
        self.n_partial += stats.n_partial

    def part(self, title: str) -> None:
        """R vignette part heading (e.g. Working with mice)."""
        self.sections.append(Section(title, "", section_kind="part"))

    def numbered_section(
        self,
        num: int,
        title: str,
        parts: list[TutorialPart],
        *,
        images: list[Path] | None = None,
        reference_images: list[Path] | None = None,
    ) -> None:
        """One numbered R vignette step with narrative and code blocks."""
        stats = SectionStats()
        body = render_tutorial_section(parts, stats)
        self._merge_stats(stats)
        ref_paths = reference_images
        if ref_paths is None and images:
            ref_paths = reference_images_for_step(self.number, num)
        self.sections.append(
            Section(
                f"{num}. {title}",
                body,
                image_paths=images or [],
                reference_image_paths=ref_paths or [],
                section_kind="step",
            )
        )

    def tutorial_plot(
        self,
        exercise: str,
        r_code: str,
        python_code: str,
        images: list[Path],
        *,
        note: str = "Matplotlib equivalent of the R lattice plot.",
    ) -> None:
        """Plot step in tutorial layout (output is the figure)."""
        self.n_partial += 1
        body = format_tutorial_step_md(
            r_code,
            python_code,
            "(plot below)",
            status="partial",
            note=note,
        )
        self.sections.append(Section(exercise, body, image_paths=images))

    def build(self) -> VignetteReport:
        total = self.n_match + self.n_mismatch + self.n_skip + self.n_partial
        if self.n_mismatch == 0 and self.n_skip == 0 and self.n_partial == 0:
            status = f"Compliant ({self.n_match}/{total} steps match R)"
        elif self.n_mismatch == 0:
            status = (
                f"Partially compliant — {self.n_match} match, "
                f"{self.n_partial} partial, {self.n_skip} skipped (R-only)"
            )
        else:
            status = (
                f"Non-compliant — {self.n_mismatch} mismatches, "
                f"{self.n_match} match, {self.n_skip} skip, {self.n_partial} partial"
            )
        meta = get_meta(self.number)
        return VignetteReport(
            number=self.number,
            slug=self.slug,
            title=self.title,
            short_title=self.short_title or meta.short_title,
            reference_title=self.reference_title or meta.reference_title,
            reference_author=self.reference_author or meta.reference_author,
            source_url=self.source_url,
            status=status,
            sections=self.sections,
            disclaimer_md=self.disclaimer_md,
            parity_overview_md=self.parity_overview_md,
            intro_md=self.intro_md,
            authors=self.authors,
            series_label=self.series_label,
        )
