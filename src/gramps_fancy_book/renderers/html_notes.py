"""Render published Gramps notes as safe HTML."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape
from typing import Any
from urllib.parse import urlsplit

import mistune

from ..domain import Note

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
_NATIVE_STYLE_NAMES = frozenset(_NATIVE_STYLE_IDS.values())


@dataclass(frozen=True)
class _StyledRange:
    name: str
    value: Any
    start: int
    end: int


def render_html_note(note: Note) -> str:
    """Render a note using controlled HTML elements and escaped text."""
    text = note.text or ""
    if not text:
        return ""

    if _is_html_code(note.type):
        return f'<pre class="note-literal">{_text(text)}</pre>\n'

    formatted = _is_formatted(note.format)
    ranges = _styled_ranges(note.styled_tags, text)
    if ranges:
        return _render_styled_text(text, ranges, formatted)
    return _render_blocks(_MARKDOWN(text), formatted=formatted)


def render_html_inline_note(note: Note) -> str:
    """Render note content as safe inline HTML for headings and cover metadata."""
    text = note.text or ""
    if not text:
        return ""

    if _is_html_code(note.type):
        return _text(text)

    formatted = _is_formatted(note.format)
    ranges = _styled_ranges(note.styled_tags, text)
    if ranges:
        return _render_styled_text(text, ranges, formatted, inline=True)

    return _render_inline_blocks(_MARKDOWN(text), formatted=formatted)


def _render_inline_blocks(tokens: Any, *, formatted: bool) -> str:
    fragments = []
    if not isinstance(tokens, list):
        return ""
    for token in tokens:
        if not isinstance(token, dict):
            continue
        kind = token.get("type")
        if kind in {"paragraph", "heading", "block_text"}:
            rendered = _render_inline(_children(token), formatted=formatted)
        elif kind in {"block_code", "block_html"}:
            raw = token.get("raw")
            rendered = _text(raw if isinstance(raw, str) else "")
        elif kind == "block_quote":
            rendered = _render_inline_blocks(_children(token), formatted=formatted)
        elif kind == "list":
            rendered = _render_inline_list(token, formatted=formatted)
        else:
            rendered = ""
        if rendered:
            fragments.append(rendered)
    return " ".join(fragments)


def _render_inline_list(token: dict[str, Any], *, formatted: bool) -> str:
    fragments = []
    for item in _children(token):
        text = _render_inline_blocks(_children(item), formatted=formatted)
        if text:
            fragments.append(text)
    return " ".join(fragments)


def _is_formatted(value: Any) -> bool:
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
        return raw_tag.get("name"), raw_tag.get("value"), raw_tag.get("ranges", ())
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
        return normalized if normalized in _NATIVE_STYLE_NAMES else ""
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
    text: str,
    ranges: tuple[_StyledRange, ...],
    formatted: bool,
    *,
    inline: bool = False,
) -> str:
    output = [] if inline else ["<p>"]
    cursor = 0
    for match in re.finditer(r"(?:\r\n|\r|\n)+", text):
        output.append(_render_styled_span(text, cursor, match.start(), ranges))
        breaks = len(re.findall(r"\r\n|\r|\n", match.group()))
        if inline:
            output.append(" ")
        elif breaks > 1:
            output.append("</p>\n")
            for _ in range(breaks - 2):
                output.append("<p></p>\n")
            output.append("<p>")
        elif formatted:
            output.append("<br>\n")
        else:
            output.append(" ")
        cursor = match.end()
    output.append(_render_styled_span(text, cursor, len(text), ranges))
    if not inline:
        output.append("</p>\n")
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
        rendered = _text(text[left:right])
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
    tags = {
        "bold": ("strong", "strong"),
        "italic": ("em", "em"),
        "underline": ("u", "u"),
        "strikethrough": ("del", "del"),
        "superscript": ("sup", "sup"),
        "subscript": ("sub", "sub"),
    }
    if item.name == "link":
        target = _href_target(item.value)
        if target is not None:
            return f'<a href="{_attr(target)}">{rendered}</a>'
        return rendered
    tag = tags.get(item.name)
    return f"<{tag[0]}>{rendered}</{tag[1]}>" if tag else rendered


def _href_target(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    if any(ord(char) < 32 for char in value):
        return None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    scheme = parsed.scheme.casefold()
    if (scheme in {"http", "https"} and parsed.netloc) or (
        scheme == "mailto" and parsed.path
    ):
        return value
    return None


def safe_html_url(value: Any) -> str | None:
    """Return a URL usable in an HTML link when its scheme is explicitly allowed."""
    return _href_target(value)


def _render_blocks(tokens: Any, *, formatted: bool, list_depth: int = 0) -> str:
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
                output.append(f"<p>{rendered}</p>\n")
        elif kind == "heading":
            attrs = token.get("attrs")
            attrs = attrs if isinstance(attrs, dict) else {}
            level = attrs.get("level", 1)
            level = level if isinstance(level, int) and not isinstance(level, bool) else 1
            tag = min(max(level + 3, 4), 6)
            output.append(
                f"<h{tag}>{_render_inline(children, formatted=formatted)}</h{tag}>\n"
            )
        elif kind == "block_quote":
            output.append("<blockquote>\n")
            output.append(
                _render_blocks(children, formatted=formatted, list_depth=list_depth)
            )
            output.append("</blockquote>\n")
        elif kind == "list":
            output.append(_render_list(token, formatted=formatted, list_depth=list_depth))
        elif kind == "block_code":
            raw = token.get("raw")
            output.append(f"<pre><code>{_text(raw if isinstance(raw, str) else '')}</code></pre>\n")
        elif kind == "block_html":
            raw = token.get("raw")
            output.append(f'<pre class="note-literal">{_text(raw if isinstance(raw, str) else "")}</pre>\n')
        elif kind == "thematic_break":
            output.append("<hr>\n")
        else:
            raw = token.get("raw")
            if isinstance(raw, str):
                output.append(f"<p>{_text(raw)}</p>\n")
            elif children:
                output.append(
                    _render_blocks(children, formatted=formatted, list_depth=list_depth)
                )
    return "".join(output)


def _render_list(token: dict[str, Any], *, formatted: bool, list_depth: int) -> str:
    attrs = token.get("attrs")
    attrs = attrs if isinstance(attrs, dict) else {}
    ordered = attrs.get("ordered") is True
    tag = "ol" if ordered else "ul"
    start = attrs.get("start", 1)
    start_attr = (
        f' start="{start}"'
        if ordered and isinstance(start, int) and not isinstance(start, bool) and start > 1
        else ""
    )
    output = [f"<{tag}{start_attr}>\n"]
    for item in _children(token):
        item_type = item.get("type")
        item_attrs = item.get("attrs")
        item_attrs = item_attrs if isinstance(item_attrs, dict) else {}
        output.append("<li>")
        if item_type == "task_list_item":
            checked = " checked" if item_attrs.get("checked") else ""
            label = "Terminé" if checked else "À faire"
            output.append(
                f'<input type="checkbox" disabled{checked} aria-label="{label}"> '
            )
        output.append(
            _render_blocks(
                _children(item),
                formatted=formatted,
                list_depth=list_depth + 1,
            )
        )
        output.append("</li>\n")
    output.append(f"</{tag}>\n")
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
            output.append(_text(raw))
        elif kind == "emphasis":
            output.append(f"<em>{rendered_children}</em>")
        elif kind == "strong":
            output.append(f"<strong>{rendered_children}</strong>")
        elif kind == "codespan":
            output.append(f"<code>{_text(raw)}</code>")
        elif kind == "link":
            attrs = token.get("attrs")
            attrs = attrs if isinstance(attrs, dict) else {}
            target = _href_target(attrs.get("url"))
            output.append(
                f'<a href="{_attr(target)}">{rendered_children}</a>'
                if target is not None
                else rendered_children
            )
        elif kind == "image":
            label = rendered_children or "image"
            output.append(f'<span class="note-image-alt">[Image : {label}]</span>')
        elif kind == "inline_html":
            output.append(_text(raw))
        elif kind in {"linebreak", "softbreak"}:
            output.append("<br>\n" if kind == "linebreak" or formatted else " ")
        elif kind == "strikethrough":
            output.append(f"<del>{rendered_children}</del>")
        elif kind == "superscript":
            output.append(f"<sup>{rendered_children}</sup>")
        elif kind == "subscript":
            output.append(f"<sub>{rendered_children}</sub>")
        elif kind in {"mark", "insert"}:
            output.append(f"<u>{rendered_children}</u>")
        elif children:
            output.append(rendered_children)
        elif raw:
            output.append(_text(raw))
    return "".join(output)


def _children(token: dict[str, Any]) -> list[dict[str, Any]]:
    children = token.get("children")
    if not isinstance(children, list):
        return []
    return [child for child in children if isinstance(child, dict)]


def _text(value: Any) -> str:
    return escape("" if value is None else str(value), quote=False)


def _attr(value: Any) -> str:
    return escape("" if value is None else str(value), quote=True)
