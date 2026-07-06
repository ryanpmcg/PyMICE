"""Markdown and HTML report builders for vignette output."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_tab_index = 0


@dataclass
class Section:
    title: str
    body_md: str
    image_paths: list[Path] = field(default_factory=list)
    reference_image_paths: list[Path] = field(default_factory=list)
    section_kind: str = "step"  # step | part


@dataclass
class VignetteReport:
    number: str
    slug: str
    title: str
    source_url: str
    status: str
    sections: list[Section] = field(default_factory=list)
    error: str | None = None
    disclaimer_md: str = ""
    parity_overview_md: str = ""
    intro_md: str = ""
    authors: str = ""
    series_label: str = ""
    short_title: str = ""
    reference_title: str = ""
    reference_author: str = ""


# Blocks for intermediate parser
class Block:
    pass


@dataclass
class HeadingBlock(Block):
    level: int
    text: str


@dataclass
class CodeBlock(Block):
    lang: str
    code: str


@dataclass
class ParaBlock(Block):
    text: str


@dataclass
class ListBlock(Block):
    items: list[str]


@dataclass
class TableBlock(Block):
    lines: list[str]


def _esc(text: str) -> str:
    return html.escape(text)


_INLINE_MD = re.compile(
    r"\*\*(.+?)\*\*"
    r"|(?<!\*)\*([^*\n]+?)\*(?!\*)"
    r"|`([^`]+)`"
    r"|\[([^\]]+)\]\(([^)]+)\)"
)


def _inline_md(text: str) -> str:
    """Bold, italic, inline code, and markdown links."""
    parts: list[str] = []
    pos = 0
    for match in _INLINE_MD.finditer(text):
        parts.append(_esc(text[pos : match.start()]))
        if match.group(1) is not None:
            parts.append(f"<strong>{_esc(match.group(1))}</strong>")
        elif match.group(2) is not None:
            parts.append(f"<em>{_esc(match.group(2))}</em>")
        elif match.group(3) is not None:
            parts.append(f"<code>{_esc(match.group(3))}</code>")
        else:
            parts.append(f'<a href="{_esc(match.group(5))}">{_esc(match.group(4))}</a>')
        pos = match.end()
    parts.append(_esc(text[pos:]))
    return "".join(parts)


def _md_table_html(lines: list[str]) -> str:
    rows = [ln.strip() for ln in lines if ln.strip()]
    if not rows:
        return ""
    header = [c.strip() for c in rows[0].strip("|").split("|")]
    body_rows = rows[2:] if len(rows) > 2 and set(rows[1]) <= {"|", "-", " "} else rows[1:]
    thead = "<tr>" + "".join(f"<th>{_esc(c)}</th>" for c in header) + "</tr>"
    tbody = ""
    for row in body_rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        tbody += "<tr>" + "".join(f"<td>{_esc(c)}</td>" for c in cells) + "</tr>"
    return f"<table><thead>{thead}</thead><tbody>{tbody}</tbody></table>"


def parse_blocks(md: str) -> list[Block]:
    lines = md.splitlines()
    blocks: list[Block] = []
    i = 0
    n = len(lines)
    while i < n:
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("```"):
            lang = stripped[3:].strip() or "text"
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < n:
                i += 1
            blocks.append(CodeBlock(lang, "\n".join(code_lines)))
            continue
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped[level:].strip()
            blocks.append(HeadingBlock(level, text))
            i += 1
            continue
        if stripped.startswith("- "):
            items = []
            while i < n and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:])
                i += 1
            blocks.append(ListBlock(items))
            continue
        if stripped.startswith("|"):
            table_lines = []
            while i < n and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            blocks.append(TableBlock(table_lines))
            continue
        # Paragraph
        para_lines = []
        while i < n:
            s = lines[i].strip()
            if not s:
                break
            if s.startswith("```"):
                break
            if s.startswith("#"):
                break
            if s.startswith("- "):
                break
            if s.startswith("|"):
                break
            para_lines.append(s)
            i += 1
        if para_lines:
            blocks.append(ParaBlock(" ".join(para_lines)))
        else:
            if i < n:
                blocks.append(ParaBlock(lines[i].strip()))
                i += 1
    return blocks


def render_dual_code_tabs(
    r_code: str, py_code: str, out_code: str, out_lang: str, r_out: str = ""
) -> str:
    global _tab_index
    _tab_index += 1
    idx = _tab_index

    r_output_html = ""
    if r_out.strip():
        r_output_html = f"""
    <div class="output-header">Console Output</div>
    <pre class="language-text"><code class="language-text">{_esc(r_out)}</code></pre>
"""

    return f"""
<div class="code-tabs" id="tabs-{idx}">
  <div class="tab-headers">
    <button class="tab-btn active" onclick="switchTab(this, 'python')">Python (PyMICE)</button>
    <button class="tab-btn" onclick="switchTab(this, 'r')">R (Reference)</button>
    <button class="tab-btn" onclick="switchTab(this, 'compare')">Side-by-Side</button>
  </div>
  <div class="tab-content python active">
    <pre class="language-python"><code class="language-python">{_esc(py_code)}</code></pre>
    <div class="output-header">Console Output</div>
    <pre class="language-{_esc(out_lang)}"><code class="language-{_esc(out_lang)}">{_esc(out_code)}</code></pre>
  </div>
  <div class="tab-content r">
    <pre class="language-r"><code class="language-r">{_esc(r_code)}</code></pre>
    {r_output_html}
  </div>
  <div class="tab-content compare">
    <div class="compare-grid">
      <div>
        <div class="compare-title">Python (PyMICE)</div>
        <pre class="language-python"><code class="language-python">{_esc(py_code)}</code></pre>
        <div class="output-header">Console Output</div>
        <pre class="language-{_esc(out_lang)}"><code class="language-{_esc(out_lang)}">{_esc(out_code)}</code></pre>
      </div>
      <div>
        <div class="compare-title">R (Reference)</div>
        <pre class="language-r"><code class="language-r">{_esc(r_code)}</code></pre>
        {r_output_html}
      </div>
    </div>
  </div>
</div>
"""


def _asset_ref(slug: str, filename: str, *, reference: bool = False) -> str:
    if reference:
        return f"assets/reference/{slug}/{filename}"
    return f"assets/{filename}"


def render_plot_tabs(
    slug: str,
    pymice_images: list[Path],
    reference_images: list[Path],
    caption: str,
) -> str:
    """Side-by-side R vs PyMICE figure switcher (Python / R / Split)."""
    global _tab_index
    _tab_index += 1
    idx = _tab_index

    def _img_block(paths: list[Path], *, reference: bool) -> str:
        if not paths:
            return '<p class="plot-empty">No figure available for this view.</p>'
        parts = []
        for path in paths:
            src = _asset_ref(slug, path.name, reference=reference)
            parts.append(
                f'<figure class="plot-figure"><img src="{_esc(src)}" alt="{_esc(caption)}">'
                f"<figcaption>{_esc(path.name)}</figcaption></figure>"
            )
        return "\n".join(parts)

    py_html = _img_block(pymice_images, reference=False)
    r_html = _img_block(reference_images, reference=True)

    if pymice_images and reference_images and len(pymice_images) == len(reference_images):
        pair_rows = []
        for py_path, ref_path in zip(pymice_images, reference_images, strict=True):
            py_src = _asset_ref(slug, py_path.name, reference=False)
            ref_src = _asset_ref(slug, ref_path.name, reference=True)
            pair_rows.append(
                f"""
    <div class="compare-grid plot-compare-grid plot-compare-pair">
      <div>
        <div class="compare-title">Python (PyMICE)</div>
        <figure class="plot-figure"><img src="{_esc(py_src)}" alt="{_esc(caption)}">
        <figcaption>{_esc(py_path.name)}</figcaption></figure>
      </div>
      <div>
        <div class="compare-title">R (Reference)</div>
        <figure class="plot-figure"><img src="{_esc(ref_src)}" alt="{_esc(caption)}">
        <figcaption>{_esc(ref_path.name)}</figcaption></figure>
      </div>
    </div>"""
            )
        compare_html = "\n".join(pair_rows)
    else:
        compare_html = f"""
    <div class="compare-grid plot-compare-grid">
      <div>
        <div class="compare-title">Python (PyMICE)</div>
        {py_html}
      </div>
      <div>
        <div class="compare-title">R (Reference)</div>
        {r_html}
      </div>
    </div>
"""

    return f"""
<div class="code-tabs plot-tabs" id="plots-{idx}">
  <div class="tab-headers">
    <button class="tab-btn active" onclick="switchTab(this, 'python')">Python (PyMICE)</button>
    <button class="tab-btn" onclick="switchTab(this, 'r')">R (Reference)</button>
    <button class="tab-btn" onclick="switchTab(this, 'compare')">Side-by-Side</button>
  </div>
  <div class="tab-content python active">
    {py_html}
  </div>
  <div class="tab-content r">
    {r_html}
  </div>
  <div class="tab-content compare">
    {compare_html}
  </div>
</div>
"""


def render_comparison_tabs(r_expected: str, py_output: str) -> str:
    global _tab_index
    _tab_index += 1
    idx = _tab_index
    return f"""
<div class="code-tabs" id="tabs-{idx}">
  <div class="tab-headers">
    <button class="tab-btn active" onclick="switchTab(this, 'python')">Python (PyMICE)</button>
    <button class="tab-btn" onclick="switchTab(this, 'r')">R (Reference)</button>
    <button class="tab-btn" onclick="switchTab(this, 'compare')">Side-by-Side</button>
  </div>
  <div class="tab-content python active">
    <div class="output-header">PyMICE Output</div>
    <pre class="language-text"><code class="language-text">{_esc(py_output)}</code></pre>
  </div>
  <div class="tab-content r">
    <div class="output-header">R Vignette Expected</div>
    <pre class="language-text"><code class="language-text">{_esc(r_expected)}</code></pre>
  </div>
  <div class="tab-content compare">
    <div class="compare-grid">
      <div>
        <div class="compare-title">PyMICE Output</div>
        <pre class="language-text"><code class="language-text">{_esc(py_output)}</code></pre>
      </div>
      <div>
        <div class="compare-title">R Vignette Expected</div>
        <pre class="language-text"><code class="language-text">{_esc(r_expected)}</code></pre>
      </div>
    </div>
  </div>
</div>
"""


def blocks_to_html(blocks: list[Block]) -> str:
    parts: list[str] = []
    i = 0
    n = len(blocks)
    while i < n:
        # Check for R-Python-Output tutorial pattern (with R output block)
        if (
            i + 7 < n
            and isinstance(blocks[i], HeadingBlock)
            and blocks[i].text.lower() == "r code"
            and isinstance(blocks[i + 1], CodeBlock)
            and isinstance(blocks[i + 2], HeadingBlock)
            and blocks[i + 2].text.lower() == "r output"
            and isinstance(blocks[i + 3], CodeBlock)
            and isinstance(blocks[i + 4], HeadingBlock)
            and blocks[i + 4].text.lower() == "python code"
            and isinstance(blocks[i + 5], CodeBlock)
            and isinstance(blocks[i + 6], HeadingBlock)
            and blocks[i + 6].text.lower() == "output"
            and isinstance(blocks[i + 7], CodeBlock)
        ):
            r_code = blocks[i + 1].code
            r_out = blocks[i + 3].code
            py_code = blocks[i + 5].code
            out_code = blocks[i + 7].code
            out_lang = blocks[i + 7].lang
            parts.append(render_dual_code_tabs(r_code, py_code, out_code, out_lang, r_out=r_out))
            i += 8
            continue

        # Check for R-Python-Output tutorial pattern (without R output block)
        if (
            i + 5 < n
            and isinstance(blocks[i], HeadingBlock)
            and blocks[i].text.lower() == "r code"
            and isinstance(blocks[i + 1], CodeBlock)
            and isinstance(blocks[i + 2], HeadingBlock)
            and blocks[i + 2].text.lower() == "python code"
            and isinstance(blocks[i + 3], CodeBlock)
            and isinstance(blocks[i + 4], HeadingBlock)
            and blocks[i + 4].text.lower() == "output"
            and isinstance(blocks[i + 5], CodeBlock)
        ):
            r_code = blocks[i + 1].code
            py_code = blocks[i + 3].code
            out_code = blocks[i + 5].code
            out_lang = blocks[i + 5].lang
            parts.append(render_dual_code_tabs(r_code, py_code, out_code, out_lang))
            i += 6
            continue

        # Check for R-Python step pattern (without output)
        if (
            i + 3 < n
            and isinstance(blocks[i], HeadingBlock)
            and blocks[i].text.lower() == "r vignette expected"
            and isinstance(blocks[i + 1], CodeBlock)
            and isinstance(blocks[i + 2], HeadingBlock)
            and blocks[i + 2].text.lower() == "pymice output"
            and isinstance(blocks[i + 3], CodeBlock)
        ):
            r_expected = blocks[i + 1].code
            py_output = blocks[i + 3].code
            parts.append(render_comparison_tabs(r_expected, py_output))
            i += 4
            continue

        block = blocks[i]
        if isinstance(block, HeadingBlock):
            tag = min(block.level + 2, 6)
            parts.append(f"<h{tag}>{_inline_md(block.text)}</h{tag}>")
        elif isinstance(block, CodeBlock):
            parts.append(
                f'<pre class="language-{_esc(block.lang)}"><code class="language-{_esc(block.lang)}">{_esc(block.code)}</code></pre>'
            )
        elif isinstance(block, ParaBlock):
            parts.append(f"<p>{_inline_md(block.text)}</p>")
        elif isinstance(block, ListBlock):
            lis = "".join(f"<li>{_inline_md(item)}</li>" for item in block.items)
            parts.append(f"<ul>{lis}</ul>")
        elif isinstance(block, TableBlock):
            parts.append(_md_table_html(block.lines))
        i += 1
    return "\n".join(parts)


def _md_to_html_paragraphs(md: str) -> str:
    """Wrapper that converts markdown to HTML via the block-based parser."""
    blocks = parse_blocks(md)
    return blocks_to_html(blocks)


def vignette_markdown(report: VignetteReport) -> str:
    vnum = int(report.number)
    display = report.short_title or report.title
    lines = [
        f"# V{vnum}: {display}",
        "",
        f"*Compare to **{report.reference_title or display}** by {report.reference_author or report.authors}*",
        "",
        f"**Reference:** {report.source_url}",
        f"**Parity status:** {report.status}",
        "",
    ]
    if report.disclaimer_md.strip():
        lines.extend([report.disclaimer_md.strip(), ""])
    if report.parity_overview_md.strip():
        lines.extend(["## Parity overview", "", report.parity_overview_md.strip(), ""])
    if report.intro_md.strip():
        lines.extend(["## Introduction", "", report.intro_md.strip(), ""])
    if report.error:
        lines.extend(["## Error", "", f"```text\n{report.error}\n```", ""])
    for section in report.sections:
        prefix = "###" if section.section_kind == "part" else "##"
        lines.extend([f"{prefix} {section.title}", "", section.body_md, ""])
        for img in section.image_paths:
            rel = img.name
            lines.append(f"![{section.title}](assets/{rel})")
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def vignette_html(report: VignetteReport, *, all_slugs: list[tuple[str, str, str, str]]) -> str:
    # Sidebar Table of Contents
    toc_links = []
    for section in report.sections:
        if section.section_kind == "part":
            toc_links.append(f'<div class="sidebar-part-title">{_esc(section.title)}</div>')
        else:
            slug = re.sub(r"[^a-zA-Z0-9_-]", "", section.title.replace(" ", "-")).lower()
            toc_links.append(
                f'<a href="#{slug}" class="sidebar-toc-link">{_esc(section.title)}</a>'
            )

    other_vignettes_links = []
    for num, slug, short_title, _nav in all_slugs:
        active_cls = " active" if slug == report.slug else ""
        n = int(num)
        other_vignettes_links.append(
            f'<a href="{_esc(slug)}.html" class="sidebar-nav-link{active_cls}">V{n}: {_esc(short_title)}</a>'
        )

    display_title = report.short_title or report.title
    vnum = int(report.number)
    ref_title = report.reference_title or display_title
    ref_author = report.reference_author or (report.authors or "the mice authors")

    parity_block_parts: list[str] = [
        f"<p><strong>Parity status:</strong> {_esc(report.status)}</p>",
    ]
    if report.disclaimer_md.strip():
        parity_block_parts.append(_md_to_html_paragraphs(report.disclaimer_md))
    if report.parity_overview_md.strip():
        parity_block_parts.append(_md_to_html_paragraphs(report.parity_overview_md))

    body_parts = [
        f"<h1>V{vnum}: {_esc(display_title)}</h1>",
        f'<p class="subtitle">Compare to <em>{_esc(ref_title)}</em> by {_esc(ref_author)}</p>',
        f'<p class="subtitle"><a href="{_esc(report.source_url)}">Open reference vignette</a></p>',
        f'<div class="parity-status-block" id="parity-status">{"".join(parity_block_parts)}</div>',
    ]
    if report.intro_md.strip():
        body_parts.append('<h2 id="introduction">Introduction</h2>')
        body_parts.append(f'<div class="intro">{_md_to_html_paragraphs(report.intro_md)}</div>')
    if report.error:
        body_parts.append(f"<h2>Error</h2><pre>{_esc(report.error)}</pre>")

    for section in report.sections:
        tag = "h3" if section.section_kind == "part" else "h2"
        slug = re.sub(r"[^a-zA-Z0-9_-]", "", section.title.replace(" ", "-")).lower()
        body_parts.append(f'<{tag} id="{slug}">{_esc(section.title)}</{tag}>')
        body_parts.append(_md_to_html_paragraphs(section.body_md))
        if section.image_paths or section.reference_image_paths:
            body_parts.append(
                render_plot_tabs(
                    report.slug,
                    section.image_paths,
                    section.reference_image_paths,
                    section.title,
                )
            )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>V{vnum}: {_esc(display_title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    :root {{
      --primary: #4f46e5;
      --primary-hover: #4338ca;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --alert-bg: #fffbeb;
      --alert-border: #fde68a;
    }}
    body {{
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      color: var(--text);
      background-color: var(--bg);
      line-height: 1.6;
      margin: 0;
      padding: 0;
    }}
    
    .app-layout {{
      display: flex;
      min-height: 100vh;
    }}
    
    .sidebar-container {{
      width: 300px;
      background: #ffffff;
      border-right: 1px solid var(--border);
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
      flex-shrink: 0;
      padding: 1.5rem;
      box-sizing: border-box;
    }}
    
    .main-container {{
      flex-grow: 1;
      padding: 2rem 3rem 4rem;
      max-width: 900px;
      box-sizing: border-box;
      min-width: 0;
    }}
    
    .back-home {{
      display: inline-flex;
      align-items: center;
      color: var(--primary);
      text-decoration: none;
      font-weight: 500;
      font-size: 0.9rem;
      margin-bottom: 1.5rem;
    }}
    .back-home:hover {{ text-decoration: underline; }}
    
    .sidebar-section-title {{
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin: 1.5rem 0 0.5rem;
    }}
    
    .sidebar-nav-link {{
      display: block;
      color: #334155;
      text-decoration: none;
      font-size: 0.85rem;
      padding: 0.35rem 0.5rem;
      border-radius: 6px;
      margin-bottom: 0.25rem;
      transition: background 0.2s;
    }}
    .sidebar-nav-link:hover {{
      background: #f1f5f9;
    }}
    .sidebar-nav-link.active {{
      background: #e0e7ff;
      color: var(--primary);
      font-weight: 600;
    }}
    
    .sidebar-part-title {{
      font-size: 0.8rem;
      font-weight: 600;
      color: #475569;
      margin: 1rem 0 0.25rem 0.5rem;
    }}
    .sidebar-toc-link {{
      display: block;
      color: #64748b;
      text-decoration: none;
      font-size: 0.8rem;
      padding: 0.2rem 0.5rem 0.2rem 1rem;
      border-left: 1px solid var(--border);
      transition: all 0.2s;
    }}
    .sidebar-toc-link:hover {{
      color: var(--primary);
      border-left-color: var(--primary);
    }}
    
    h1, h2, h3, h4 {{
      font-family: 'Outfit', sans-serif;
      color: #0f172a;
      font-weight: 600;
    }}
    h1 {{ font-size: 2.25rem; margin-top: 0; margin-bottom: 0.5rem; }}
    h2 {{ font-size: 1.5rem; margin-top: 2.5rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; scroll-margin-top: 2rem; }}
    h3 {{ font-size: 1.15rem; margin-top: 1.75rem; margin-bottom: 0.75rem; scroll-margin-top: 2rem; }}
    
    p {{ margin-top: 0; margin-bottom: 1rem; }}
    .meta {{ color: var(--text-muted); margin-bottom: 1.5rem; }}
    .subtitle {{
      color: var(--text-muted);
      font-size: 0.95rem;
      margin: 0.15rem 0 0.35rem;
      line-height: 1.45;
    }}
    .subtitle a {{ color: var(--primary); text-decoration: none; font-weight: 500; }}
    .subtitle a:hover {{ text-decoration: underline; }}
    .parity-status-block {{
      background: var(--alert-bg);
      border: 1px solid var(--alert-border);
      border-radius: 8px;
      padding: 1.25rem;
      margin: 1.25rem 0 2rem;
      font-size: 0.9rem;
    }}
    .parity-status-block p:first-child {{ margin-top: 0; }}
    
    /* Code and tabs styling */
    .code-tabs {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      margin: 1.5rem 0;
      overflow: hidden;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }}
    .tab-headers {{
      display: flex;
      background: #f8fafc;
      border-bottom: 1px solid var(--border);
      padding: 0.25rem 0.5rem 0;
    }}
    .tab-btn {{
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      padding: 0.5rem 1rem;
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.2s;
    }}
    .tab-btn:hover {{ color: var(--text); }}
    .tab-btn.active {{
      color: var(--primary);
      border-bottom-color: var(--primary);
    }}
    .tab-content {{ display: none; padding: 1rem; }}
    .tab-content.active {{ display: block; }}
    
    .compare-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 1.5rem;
    }}
    .compare-title {{
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 0.5rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .output-header {{
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-muted);
      margin-top: 1rem;
      margin-bottom: 0.25rem;
    }}
    
    pre[class*="language-"] {{
      margin: 0 !important;
      border-radius: 6px !important;
      font-size: 0.85rem !important;
      overflow-x: auto !important;
      max-width: 100%;
    }}
    
    pre {{
      background: #0f172a;
      color: #f8fafc;
      padding: 1rem;
      border-radius: 8px;
      overflow-x: auto !important;
      max-width: 100%;
      font-family: 'Fira Code', monospace;
      font-size: 0.85rem;
      margin: 1rem 0;
    }}
    
    /* Custom Scrollbar for pre, sidebars, and tab content */
    pre::-webkit-scrollbar, 
    .sidebar-container::-webkit-scrollbar, 
    pre[class*="language-"]::-webkit-scrollbar {{
      height: 8px;
      width: 6px;
    }}
    pre::-webkit-scrollbar-track, 
    .sidebar-container::-webkit-scrollbar-track, 
    pre[class*="language-"]::-webkit-scrollbar-track {{
      background: transparent;
    }}
    pre::-webkit-scrollbar-thumb, 
    .sidebar-container::-webkit-scrollbar-thumb, 
    pre[class*="language-"]::-webkit-scrollbar-thumb {{
      background: #cbd5e1;
      border-radius: 9999px;
    }}
    pre::-webkit-scrollbar-thumb:hover, 
    .sidebar-container::-webkit-scrollbar-thumb:hover, 
    pre[class*="language-"]::-webkit-scrollbar-thumb:hover {{
      background: #94a3b8;
    }}
    
    pre code {{
      font-family: 'Fira Code', monospace;
    }}
    
    code {{
      font-family: 'Fira Code', monospace;
      font-size: 0.85rem;
      background: #f1f5f9;
      color: #0f172a;
      padding: 0.15em 0.3em;
      border-radius: 4px;
    }}
    pre code {{ background: transparent; color: inherit; padding: 0; border-radius: 0; }}
    
    /* Table styling */
    table {{
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      margin: 1.5rem 0;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      background: #ffffff;
    }}
    th, td {{ padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid var(--border); }}
    th {{ background: #f8fafc; font-weight: 600; font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }}
    tr:last-child td {{ border-bottom: none; }}
    
    /* Image and Figures */
    figure, figure.plot-figure {{ margin: 1rem 0; background: #ffffff; border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }}
    img {{ max-width: 100%; height: auto; border-radius: 4px; display: block; margin: 0 auto; }}
    figcaption {{ font-size: 0.8rem; color: var(--text-muted); text-align: center; margin-top: 0.5rem; }}
    .plot-tabs {{ margin-top: 1.25rem; }}
    .plot-compare-grid figure {{ margin: 0; }}
    .plot-empty {{ color: var(--text-muted); font-size: 0.9rem; font-style: italic; }}
    
  </style>
</head>
<body>
  <div class="app-layout">
    <div class="sidebar-container">
      <a href="index.html" class="back-home">← Back to index</a>
      
      <div class="sidebar-section-title">Vignettes</div>
      {"".join(other_vignettes_links)}
      
      <div class="sidebar-section-title">Table of Contents</div>
      {"".join(toc_links)}
    </div>
    
    <div class="main-container">
      {"".join(body_parts)}
    </div>
  </div>
  
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
  <script>
    function switchTab(btn, mode) {{
      const container = btn.closest('.code-tabs');
      // Update buttons
      container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      // Update content
      container.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      container.querySelector('.tab-content.' + mode).classList.add('active');
    }}
  </script>
</body>
</html>
"""


def index_markdown(
    reports: list[VignetteReport],
    pytest_text: str,
    generated_at: datetime,
) -> str:
    lines = [
        "# PyMICE vignette report",
        "",
        f"Generated: {generated_at.isoformat()}",
        "",
        "## Vignettes",
        "",
        "| # | Title | Status | Report |",
        "|---|-------|--------|--------|",
    ]
    for r in reports:
        status = r.status if not r.error else f"ERROR: {r.error[:40]}..."
        vnum = int(r.number)
        label = r.short_title or r.title
        lines.append(
            f"| V{vnum} | {label} | {status} | [{r.slug}.md]({r.slug}.md) / [HTML]({r.slug}.html) |"
        )
    lines.extend(["", "## Test suite (pytest)", "", "```text", pytest_text.strip(), "```", ""])
    return "\n".join(lines)


def index_html(
    reports: list[VignetteReport],
    pytest_text: str,
    generated_at: datetime,
) -> str:
    rows = ""
    for r in reports:
        cls = (
            "ok"
            if r.error is None and "compliant" in r.status.lower()
            else ("skip" if "partial" in r.status.lower() else "fail")
        )
        if "non-compliant" in r.status.lower():
            cls = "fail"
        if r.error:
            cls = "fail"
        vnum = int(r.number)
        label = r.short_title or r.title
        rows += (
            f"<tr><td>V{vnum}</td><td>{_esc(label)}</td>"
            f'<td><span class="badge {cls}">{_esc(r.status)}</span></td>'
            f'<td><a href="{_esc(r.slug)}.html" class="action-link">View Report (HTML)</a> · <a href="{_esc(r.slug)}.md" class="action-link">MD</a></td></tr>'
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PyMICE vignette report</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #4f46e5;
      --primary-hover: #4338ca;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
    }}
    body {{
      font-family: 'Inter', system-ui, sans-serif;
      max-width: 1000px;
      margin: 0 auto;
      padding: 3rem 1.5rem;
      line-height: 1.5;
      background-color: var(--bg);
      color: var(--text);
    }}
    
    h1, h2, h3 {{
      font-family: 'Outfit', sans-serif;
      color: #0f172a;
    }}
    h1 {{ font-size: 2.5rem; margin-top: 0; margin-bottom: 0.5rem; }}
    h2 {{ font-size: 1.5rem; margin-top: 3rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }}
    
    .meta-time {{
      color: var(--text-muted);
      margin-bottom: 2.5rem;
      font-size: 0.9rem;
    }}
    
    table {{
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      margin: 1.5rem 0;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      background: var(--card-bg);
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }}
    th, td {{
      padding: 1rem;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }}
    th {{
      background: #f8fafc;
      font-weight: 600;
      font-size: 0.85rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    tr:last-child td {{ border-bottom: none; }}
    
    .badge {{
      display: inline-flex;
      align-items: center;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
    }}
    .badge.ok {{ background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }}
    .badge.skip {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}
    .badge.fail {{ background: #ffe4e6; color: #991b1b; border: 1px solid #fecdd3; }}
    
    .action-link {{
      color: var(--primary);
      text-decoration: none;
      font-weight: 500;
    }}
    .action-link:hover {{ text-decoration: underline; }}
    
    pre, code {{ font-family: 'Fira Code', monospace; font-size: 0.85rem; }}
    code {{ background: #e2e8f0; padding: 0.15em 0.35em; border-radius: 4px; color: #0f172a; }}
    pre {{ background: #0f172a; color: #f8fafc; padding: 1.25rem; overflow-x: auto !important; max-width: 100%; border-radius: 8px; border: 1px solid var(--border); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
    pre code {{ background: transparent; padding: 0; color: inherit; }}

    /* Custom Scrollbar */
    pre::-webkit-scrollbar {{
      height: 8px;
      width: 6px;
    }}
    pre::-webkit-scrollbar-track {{
      background: transparent;
    }}
    pre::-webkit-scrollbar-thumb {{
      background: #cbd5e1;
      border-radius: 9999px;
    }}
    pre::-webkit-scrollbar-thumb:hover {{
      background: #94a3b8;
    }}
  </style>
</head>
<body>
  <h1>PyMICE Vignette Reports</h1>
  <p class="meta-time">Generated: {_esc(generated_at.isoformat())}</p>
  <p>This dashboard contains the parity reports for PyMICE (Python FCS MICE implementation) validated against the original R <code>mice</code> vignettes outputs.</p>
  
  <h2>Verification Catalog</h2>
  <table>
    <thead><tr><th>#</th><th>Title</th><th>Parity Status</th><th>Links</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  
  <h2>Test Suite Output (pytest)</h2>
  <pre><code>{_esc(pytest_text.strip())}</code></pre>
</body>
</html>
"""


def write_reports(
    output_dir: Path,
    reports: list[VignetteReport],
    pytest_text: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    assets = output_dir / "assets"
    assets.mkdir(exist_ok=True)

    from lib.figure_map import copy_reference_assets
    from lib.vignette_catalog import get_meta, nav_label

    nav = [
        (r.number, r.slug, r.short_title or r.title, nav_label(get_meta(r.number))) for r in reports
    ]
    generated_at = datetime.now(timezone.utc)
    copy_reference_assets(assets)

    for report in reports:
        md_path = output_dir / f"{report.slug}.md"
        html_path = output_dir / f"{report.slug}.html"
        md_path.write_text(vignette_markdown(report), encoding="utf-8")
        html_path.write_text(vignette_html(report, all_slugs=nav), encoding="utf-8")

    (output_dir / "index.md").write_text(
        index_markdown(reports, pytest_text, generated_at),
        encoding="utf-8",
    )
    (output_dir / "index.html").write_text(
        index_html(reports, pytest_text, generated_at),
        encoding="utf-8",
    )
