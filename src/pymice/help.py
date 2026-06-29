"""Interactive help for PyMICE topics (R ``help()`` / ``?topic`` analogue)."""

from __future__ import annotations

import textwrap
from collections.abc import Callable
from typing import Any

from pymice.help_pages import PAGES, HelpPage, resolve_topic


def _format_page(page: HelpPage, width: int = 72) -> str:
    lines: list[str] = []
    header = f"{page.title}({page.kind})"
    lines.append(header)
    lines.append("=" * len(header))
    lines.append("")
    lines.append("Description")
    lines.append("-----------")
    lines.extend(textwrap.wrap(page.description, width=width))
    lines.append("")

    if page.usage:
        lines.append("Usage")
        lines.append("-----")
        lines.extend(page.usage.splitlines())
        lines.append("")

    if page.variables:
        lines.append("Variables")
        lines.append("---------")
        for name, desc in page.variables:
            lines.append(f"  {name:<10} {desc}")
        lines.append("")

    if page.parameters:
        lines.append("Parameters")
        lines.append("----------")
        for name, desc in page.parameters:
            wrapped = textwrap.wrap(
                desc, width=width - 12, initial_indent="    ", subsequent_indent="    "
            )
            lines.append(f"  {name}")
            lines.extend(wrapped)
        lines.append("")

    if page.details:
        lines.append("Details")
        lines.append("-------")
        lines.extend(textwrap.wrap(page.details, width=width))
        lines.append("")

    if page.source:
        lines.append("Source")
        lines.append("------")
        lines.extend(textwrap.wrap(page.source, width=width))
        lines.append("")

    if page.see_also:
        lines.append("See Also")
        lines.append("--------")
        lines.append("  " + ", ".join(page.see_also))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _topic_key(topic: str | Callable[..., Any] | type | None) -> str:
    if topic is None:
        return "__package__"
    if isinstance(topic, str):
        resolved = resolve_topic(topic)
        if resolved is None:
            raise KeyError(topic)
        return resolved
    name = getattr(topic, "__name__", None)
    if name is None:
        raise TypeError(f"cannot resolve help topic from {type(topic)!r}")
    resolved = resolve_topic(name)
    if resolved is None:
        raise KeyError(name)
    return resolved


def help(
    topic: str | Callable[..., Any] | type | None = None,
    *,
    print_: bool = True,
    width: int = 72,
) -> str:
    """
    Display documentation for a PyMICE dataset or function.

    Analogous to R ``help(topic)`` and ``?topic``. With no argument, shows the
    package overview.

    Parameters
    ----------
    topic
        Topic name (e.g. ``'nhanes'``, ``'mice'``, ``'ampute'``), or a callable
        whose ``__name__`` is looked up (e.g. ``help(mice)`` after import).
    print_
        If True (default), print the page to stdout.
    width
        Wrap width for prose sections.

    Returns
    -------
    str
        Formatted help text.
    """
    key = _topic_key(topic)
    text = _format_page(PAGES[key], width=width)
    if print_:
        print(text, end="")
    return text


def help_topics() -> list[str]:
    """Return sorted names of documented help topics."""
    seen: set[str] = set()
    out: list[str] = []
    for key, page in PAGES.items():
        if key == "__package__":
            continue
        label = page.title
        if label not in seen:
            seen.add(label)
            out.append(label)
    return sorted(out, key=str.lower)
