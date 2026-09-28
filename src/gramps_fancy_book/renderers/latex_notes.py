"""Render published Gramps notes as safe LaTeX."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlsplit

import mistune

from ..domain import Note
from .latex_text import escape_latex_text

# Markdown is parsed into tokens only. This renderer never accepts generated HTML
# or user-provided LaTeX as executable output.
_MARKDOWN = mistune.create_markdown(
    renderer="ast",
    plugins=[
        "insert",
        "mark",
        "strikethrough",
        "subscript",
        "superscript",
        "task_lists",
        "url",
    ],
)

_NATIVE_STYLE_IDS = {
    0: "bold",
    1: "italic",
    2: "underline",
    7: "superscript",
    8: "link",
    9: "strikethrough",
    10: "subscript",
}
_NATIVE_STYLE_NAMES = frozenset(
    {"bold", "italic", "underline", "superscript", "link", "strikethrough", "subscript"}
)
_STYLE_ALIASES = {
    "bold": "bold",
    "italic": "italic",
    "underline": "underline",
    "superscript": "superscript",
    "link": "link",
    "strikethrough": "strikethrough",
    "subscript": "subscript",
}


@dataclass(frozen=True)
class _StyledRange:
    name: str
    value: Any
    start: int
    end: int


def render_latex_note(note: Note) -> str:
    """Render one note without mixing Markdown and native Gramps styles."""
    text = note.text or ""
    if not text:
        return r"\emph{No text supplied.}"

    formatted = _is_formatted(note.format)
    if _is_html_code(note.type):
        return _render_styled_text(text, (), formatted)

    native_ranges = _styled_ranges(note.styled_tags, text)
    if native_ranges:
        return _render_styled_text(text, native_ranges, formatted)

    return _render_blocks(_MARKDOWN(text), formatted=formatted)


def _is_formatted(value: Any) -> bool:
    """Return whether Gramps marks the note as preserving line breaks."""
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value == 1
    if isinstance(value, str):
        return value.strip().casefold() in {"1", "formatted", "preformatted"}
    if isinstance(value, (tuple, list)):
        return any(_is_formatted(item) for item in value)
    if isinstance(value, dict):
        return any(_is_formatted(value.get(key)) for key in ("value", "string", "name"))
    return False


def _is_html_code(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value == 24
    if isinstance(value, str):
        normalized = "".join(char for char in value.casefold() if char.isalnum())
        return normalized == "htmlcode"
    if isinstance(value, (tuple, list)):
        return any(_is_html_code(item) for item in value)
    if isinstance(value, dict):
        return any(_is_html_code(value.get(key)) for key in ("value", "string", "name"))
    return False


def _styled_ranges(raw_tags: Any, text: str) -> tuple[_StyledRange, ...]:
    ranges = []
    if not isinstance(raw_tags, (tuple, list)):
        return ()
    for raw_tag in raw_tags:
        name, value, tag_ranges = _tag_parts(raw_tag)
        style = _style_name(name)
        if style not in _NATIVE_STYLE_NAMES:
            continue
        if style != "link" and value is False:
            continue
        if not isinstance(tag_ranges, (tuple, list)):
            continue
        if style == "link" and _href_target(value) is None:
            continue
        for item in tag_ranges:
            if not isinstance(item, (tuple, list)) or len(item) != 2:
                continue
            start, end = item
            if (
                isinstance(start, bool)
                or isinstance(end, bool)
                or not isinstance(start, int)
                or not isinstance(end, int)
            ):
                continue
            start = max(0, start)
            end = min(len(text), end)
            if start < end:
                ranges.append(_StyledRange(style, value, start, end))
    return tuple(ranges)


def _tag_parts(raw_tag: Any) -> tuple[Any, Any, Any]:
    if isinstance(raw_tag, dict):
        return (
            raw_tag.get("name"),
            raw_tag.get("value"),
            raw_tag.get("ranges", ()),
        )
    if isinstance(raw_tag, (tuple, list)) and len(raw_tag) >= 3:
        return raw_tag[0], raw_tag[1], raw_tag[2]
    return None, None, ()


def _style_name(value: Any) -> str:
    if isinstance(value, bool):
        return ""
    if isinstance(value, int):
        return _NATIVE_STYLE_IDS.get(value, "")
    if isinstance(value, str):
        normalized = "".join(char for char in value.casefold() if char.isalnum())
        return _STYLE_ALIASES.get(normalized, "")
    if isinstance(value, (tuple, list)):
        for item in reversed(value):
            name = _style_name(item)
            if name:
                return name
    if isinstance(value, dict):
        for key in ("string", "name", "value"):
            name = _style_name(value.get(key))
            if name:
                return name
    return ""


def _render_styled_text(
    text: str, ranges: tuple[_StyledRange, ...], formatted: bool
) -> str:
    output = []
    cursor = 0
    for match in re.finditer(r"(?:\r\n|\r|\n)+", text):
        output.append(_render_styled_span(text, cursor, match.start(), ranges))
        breaks = len(re.findall(r"\r\n|\r|\n", match.group()))
        if breaks > 1:
            output.append("\\par\n")
        elif formatted:
            output.append("\\\\\n")
        else:
            output.append(" ")
        cursor = match.end()
    output.append(_render_styled_span(text, cursor, len(text), ranges))
    return "".join(output)


def _render_styled_span(
    text: str, start: int, end: int, ranges: tuple[_StyledRange, ...]
) -> str:
    if start >= end:
        return ""
    boundaries = {start, end}
    for item in ranges:
        if start < item.start < end:
            boundaries.add(item.start)
        if start < item.end < end:
            boundaries.add(item.end)

    points = sorted(boundaries)
    output = []
    for left, right in zip(points, points[1:]):
        rendered = escape_latex_text(text[left:right])
        seen = set()
        active = []
        for item in ranges:
            if item.name not in seen and item.start <= left and right <= item.end:
                seen.add(item.name)
                active.append(item)
        for item in reversed(active):
            rendered = _wrap_native_style(item, rendered)
        output.append(rendered)
    return "".join(output)


def _wrap_native_style(item: _StyledRange, rendered: str) -> str:
    if item.name == "bold":
        return f"\\textbf{{{rendered}}}"
    if item.name == "italic":
        return f"\\emph{{{rendered}}}"
    if item.name == "underline":
        return f"\\underline{{{rendered}}}"
    if item.name == "strikethrough":
        return f"\\sout{{{rendered}}}"
    if item.name == "superscript":
        return f"\\textsuperscript{{{rendered}}}"
    if item.name == "subscript":
        return f"\\textsubscript{{{rendered}}}"
    if item.name == "link":
        target = _href_target(item.value)
        if target is not None:
            return f"\\href{{{target}}}{{{rendered}}}"
    return rendered


def _href_target(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    scheme = parsed.scheme.casefold()
    if not (
        (scheme in {"http", "https"} and parsed.netloc)
        or (scheme == "mailto" and parsed.path)
    ):
        return None
    normalized = quote(value, safe=":/?#[]@!$&'()*+,;=%")
    return f"\\detokenize{{{normalized}}}"


def _render_blocks(
    tokens: Any, *, formatted: bool, list_depth: int = 0
) -> str:
    if not isinstance(tokens, list):
        return ""
    output = []
    for token in tokens:
        if not isinstance(token, dict):
            continue
        kind = token.get("type")
        children = _children(token)
        if kind == "blank_line":
            continue
        if kind == "block_text":
            output.append(_render_inline(children, formatted=formatted))
        elif kind == "paragraph":
            rendered = _render_inline(children, formatted=formatted)
            if rendered:
                output.append(rendered + "\\par\n")
        elif kind == "heading":
            attrs = token.get("attrs")
            attrs = attrs if isinstance(attrs, dict) else {}
            level = attrs.get("level", 2)
            level = level if isinstance(level, int) and not isinstance(level, bool) else 2
            style = (
                r"\Large\bfseries",
                r"\large\bfseries",
                r"\normalsize\bfseries",
                r"\normalsize\itshape",
                r"\small\bfseries",
                r"\small\itshape",
            )[min(max(level, 1), 6) - 1]
            output.append(
                "\n\\par\\medskip\n\\noindent{"
                + style
                + " "
                + _render_inline(children, formatted=formatted)
                + "}\\par\\smallskip\n"
            )
        elif kind == "block_quote":
            output.append("\\begin{quote}\n")
            output.append(
                _render_blocks(children, formatted=formatted, list_depth=list_depth)
            )
            output.append("\\end{quote}\n")
        elif kind == "list":
            output.append(_render_list(token, formatted=formatted, list_depth=list_depth))
        elif kind in {"block_code", "block_html"}:
            raw = token.get("raw")
            output.append(_render_literal_block(raw if isinstance(raw, str) else ""))
        elif kind == "thematic_break":
            output.append("\\par\\smallskip\\hrule\\smallskip\n")
        else:
            raw = token.get("raw")
            if isinstance(raw, str):
                output.append(escape_latex_text(raw) + "\\par\n")
            elif children:
                output.append(
                    _render_blocks(children, formatted=formatted, list_depth=list_depth)
                )
    return "".join(output)


def _render_list(token: dict[str, Any], *, formatted: bool, list_depth: int) -> str:
    attrs = token.get("attrs")
    attrs = attrs if isinstance(attrs, dict) else {}
    ordered = attrs.get("ordered") is True
    environment = "enumerate" if ordered else "itemize"
    output = [f"\\begin{{{environment}}}\n"]
    if ordered:
        start = attrs.get("start", 1)
        counters = ("enumi", "enumii", "enumiii", "enumiv")
        if (
            isinstance(start, int)
            and not isinstance(start, bool)
            and 1 < start < 10000
        ):
            counter = counters[min(list_depth, len(counters) - 1)]
            output.append(f"\\setcounter{{{counter}}}{{{start - 1}}}\n")
    for item in _children(token):
        item_type = item.get("type")
        item_attrs = item.get("attrs")
        item_attrs = item_attrs if isinstance(item_attrs, dict) else {}
        if item_type == "task_list_item":
            marker = r"\item[\texttt{[x]}] " if item_attrs.get("checked") else r"\item[\texttt{[ ]}] "
            output.append(marker)
        else:
            output.append("\\item ")
        output.append(
            _render_blocks(
                _children(item),
                formatted=formatted,
                list_depth=list_depth + 1,
            )
        )
        output.append("\n")
    output.append(f"\\end{{{environment}}}\n")
    return "".join(output)


def _render_literal_block(text: str) -> str:
    output = ["\\begin{quote}\\small\n"]
    for line in text.splitlines() or [""]:
        if line:
            rendered = escape_latex_text(line).replace(" ", r"\ ")
            output.append(f"\\noindent\\texttt{{{rendered}}}\\\\\n")
        else:
            output.append("\\mbox{}\\\\\n")
    output.append("\\end{quote}\n")
    return "".join(output)


def _render_inline(tokens: Any, *, formatted: bool) -> str:
    if not isinstance(tokens, list):
        return ""
    output = []
    for token in tokens:
        if not isinstance(token, dict):
            continue
        kind = token.get("type")
        raw = token.get("raw")
        raw = raw if isinstance(raw, str) else ""
        children = _children(token)
        rendered_children = _render_inline(children, formatted=formatted)
        if kind == "text":
            output.append(escape_latex_text(raw))
        elif kind == "emphasis":
            output.append(f"\\emph{{{rendered_children}}}")
        elif kind == "strong":
            output.append(f"\\textbf{{{rendered_children}}}")
        elif kind == "codespan":
            output.append(f"\\texttt{{{escape_latex_text(raw)}}}")
        elif kind == "link":
            attrs = token.get("attrs")
            attrs = attrs if isinstance(attrs, dict) else {}
            target = _href_target(attrs.get("url"))
            output.append(
                f"\\href{{{target}}}{{{rendered_children}}}"
                if target is not None
                else rendered_children
            )
        elif kind == "image":
            label = rendered_children or "image"
            output.append(f"\\emph{{[Image: {label}]}}")
        elif kind == "inline_html":
            output.append(escape_latex_text(raw))
        elif kind in {"linebreak", "softbreak"}:
            output.append("\\\\\n" if kind == "linebreak" or formatted else " ")
        elif kind == "strikethrough":
            output.append(f"\\sout{{{rendered_children}}}")
        elif kind == "superscript":
            output.append(f"\\textsuperscript{{{rendered_children}}}")
        elif kind == "subscript":
            output.append(f"\\textsubscript{{{rendered_children}}}")
        elif kind in {"mark", "insert"}:
            output.append(f"\\underline{{{rendered_children}}}")
        else:
            if children:
                output.append(rendered_children)
            elif raw:
                output.append(escape_latex_text(raw))
    return "".join(output)


def _children(token: dict[str, Any]) -> list[dict[str, Any]]:
    children = token.get("children")
    if not isinstance(children, list):
        return []
    return [child for child in children if isinstance(child, dict)]
