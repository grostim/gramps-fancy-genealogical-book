"""Text and URL escaping for LaTeX output."""

from urllib.parse import quote, urlsplit


def escape_latex_text(value: str) -> str:
    """Escape user supplied text so it cannot introduce LaTeX commands."""
    return value.translate(_TEXT_TRANSLATION)


def format_latex_url(value: str) -> str:
    """Render an HTTP(S) URL safely, preserving its usable link characters."""
    try:
        parsed = urlsplit(value.strip())
    except ValueError:
        return escape_latex_text(value)
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.netloc:
        return escape_latex_text(value)
    normalized = quote(value.strip(), safe=":/?#[]@!$&'()*+,;=%")
    authority_start = normalized.find("://") + 3
    authority_end = len(normalized)
    for delimiter in "/?#":
        index = normalized.find(delimiter, authority_start)
        if index >= 0:
            authority_end = min(authority_end, index)
    authority = normalized[:authority_end]
    suffix = normalized[authority_end:]
    return (
        f"\\bookurl{{{_escape_latex_url(normalized)}}}"
        f"{{{_escape_latex_url(authority)}}}"
        f"{{{_escape_latex_url(suffix)}}}"
    )


def _escape_latex_url(value: str) -> str:
    """Protect characters TeX treats as comments or macro parameters."""
    return value.replace("%", r"\%").replace("#", r"\#")


_TEXT_ESCAPE = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}
_TEXT_TRANSLATION = str.maketrans(_TEXT_ESCAPE)
