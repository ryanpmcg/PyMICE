#!/usr/bin/env python3
"""Extract narrative prose and numbered steps from knitr vignette HTML snapshots."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"


def _strip_tags(text: str) -> str:
    text = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<em>(.*?)</em>", r"*\1*", text, flags=re.DOTALL)
    text = re.sub(r"<strong>(.*?)</strong>", r"**\1**", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).replace("\xa0", " ").strip()


def _extract_knitr_exercise_prose(body: str) -> dict[str, object]:
    """Parse gerkovink-style vignettes with h5 parts and **N.** step headings."""
    intro_parts: list[str] = []
    steps: list[dict[str, str]] = []
    current_part: str | None = None
    current_step: dict[str, str] | None = None

    for chunk in re.split(r"(<h5[^>]*>.*?</h5>)", body, flags=re.DOTALL):
        h5_m = re.match(r"<h5[^>]*>(.*?)</h5>", chunk, flags=re.DOTALL)
        if h5_m:
            if current_step:
                steps.append(current_step)
                current_step = None
            current_part = _strip_tags(h5_m.group(1))
            continue

        for token in re.split(
            r"(<p[^>]*>.*?</p>|<pre[^>]*>.*?</pre>|<hr\s*/?>)", chunk, flags=re.DOTALL
        ):
            if not token.strip() or token.startswith("<hr"):
                continue
            p_m = re.match(r"<p[^>]*>(.*?)</p>", token, flags=re.DOTALL)
            if p_m:
                text = _strip_tags(p_m.group(1))
                if not text:
                    continue
                step_m = re.match(r"^\*\*(\d+)\.\s*(.*?)\*\*\s*$", text, flags=re.DOTALL)
                if step_m:
                    if current_step:
                        steps.append(current_step)
                    current_step = {
                        "part": current_part or "",
                        "number": step_m.group(1),
                        "title": step_m.group(2).strip(),
                        "narrative": "",
                    }
                elif current_step is not None:
                    sep = "\n\n" if current_step["narrative"] else ""
                    current_step["narrative"] += sep + text
                else:
                    intro_parts.append(text)
                continue
            pre_m = re.match(
                r'<pre[^>]*class="[^"]*r[^"]*"[^>]*>(.*?)</pre>', token, flags=re.DOTALL
            )
            if pre_m and current_step is not None:
                code = _strip_tags(pre_m.group(1))
                current_step["r_code"] = (
                    current_step.get("r_code", "")
                    + ("\n\n" if current_step.get("r_code") else "")
                    + code
                )

    if current_step:
        steps.append(current_step)

    return {"intro": "\n\n".join(intro_parts), "steps": steps}


def _paragraphs_before_code(section_html: str) -> str:
    """Collect narrative <p> text before the first code block in a section."""
    chunks: list[str] = []
    for token in re.split(
        r"(<p[^>]*>.*?</p>|<pre[^>]*>.*?</pre>|<div class=\"sourceCode\".*?</div>)",
        section_html,
        flags=re.DOTALL,
    ):
        if token.startswith("<pre") or token.startswith('<div class="sourceCode"'):
            break
        p_m = re.match(r"<p[^>]*>(.*?)</p>", token, flags=re.DOTALL)
        if p_m:
            text = _strip_tags(p_m.group(1))
            if text:
                chunks.append(text)
    return "\n\n".join(chunks)


def _extract_article_prose(body: str) -> dict[str, object]:
    """Parse article-style vignettes (h3 parts, h4 subsections) such as ampute/futuremice."""
    intro_parts: list[str] = []
    steps: list[dict[str, str]] = []
    step_num = 0

    h3_blocks = re.split(r'(<div[^>]*class="section level3"[^>]*>)', body, flags=re.DOTALL)
    first_h3 = True
    for i in range(1, len(h3_blocks), 2):
        section = h3_blocks[i] + (h3_blocks[i + 1] if i + 1 < len(h3_blocks) else "")
        h3_m = re.search(r"<h3[^>]*>(.*?)</h3>", section, flags=re.DOTALL)
        if not h3_m:
            continue
        part_title = _strip_tags(h3_m.group(1))
        if part_title.lower() == "references":
            break

        level4_blocks = re.split(r'<div[^>]*class="section level4"[^>]*>', section, flags=re.DOTALL)
        has_h4 = any(
            re.search(r"<h4[^>]*>.*?</h4>", block, flags=re.DOTALL) for block in level4_blocks[1:]
        )

        if not has_h4:
            section_body = section.split("</h3>", 1)[-1]
            has_code = bool(
                re.search(
                    r'<pre[^>]*class="[^"]*r[^"]*"|class="sourceCode"',
                    section_body,
                    flags=re.DOTALL,
                )
            )
            narrative = _paragraphs_before_code(section_body)
            if has_code:
                step_num += 1
                steps.append(
                    {
                        "part": part_title,
                        "number": str(step_num),
                        "title": part_title,
                        "narrative": narrative,
                    }
                )
                first_h3 = False
                continue
            if first_h3 and narrative:
                intro_parts.append(narrative)
            first_h3 = False
            continue

        first_h3 = False
        for block in level4_blocks[1:]:
            h4_m = re.search(r"<h4[^>]*>(.*?)</h4>", block, flags=re.DOTALL)
            if not h4_m:
                continue
            step_num += 1
            step_title = _strip_tags(h4_m.group(1))
            after_h4 = block.split("</h4>", 1)[-1]
            narrative = _paragraphs_before_code(after_h4)
            steps.append(
                {
                    "part": part_title,
                    "number": str(step_num),
                    "title": step_title,
                    "narrative": narrative,
                }
            )

    return {"intro": "\n\n".join(intro_parts), "steps": steps}


def extract_prose_from_html(html_text: str) -> dict[str, object]:
    """Parse main content blocks from a mice vignette HTML file."""
    start = html_text.find('<h1 class="title')
    if start < 0:
        start = html_text.find("<h1")
    end = html_text.find("</body>")
    body = html_text[start:end] if start >= 0 else html_text

    title_m = re.search(r"<h1[^>]*>(.*?)</h1>", body, flags=re.DOTALL)
    title = _strip_tags(title_m.group(1)) if title_m else ""

    knitr = _extract_knitr_exercise_prose(body)
    if knitr["steps"]:
        return {"title": title, "intro": knitr["intro"], "steps": knitr["steps"]}

    article = _extract_article_prose(body)
    return {"title": title, "intro": article["intro"], "steps": article["steps"]}


def main() -> int:
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1:]]
    else:
        paths = sorted(REFERENCE.glob("*/vignette.html"))

    for path in paths:
        data = extract_prose_from_html(path.read_text(encoding="utf-8", errors="replace"))
        out = path.parent / "vignette_prose.json"
        import json

        out.write_text(json.dumps(data, indent=2), encoding="utf-8")
        rel = out.relative_to(ROOT) if out.is_relative_to(ROOT) else out
        print(f"Wrote {rel} ({len(data['steps'])} steps)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
