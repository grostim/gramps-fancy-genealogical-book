"""Minimal LaTeX renderer proving the shared model contract."""

from urllib.parse import quote, urlsplit

from ..domain import BookModel


def render_latex(model: BookModel) -> str:
    family = model.reference_family
    escaped = escape_latex_text(family.handle)
    return (
        "\\documentclass{article}\n\\usepackage[hidelinks]{hyperref}\n"
        "\\begin{document}\n"
        f"\\section*{{{escaped}}}\n"
        "\\end{document}\n"
    )


def escape_latex_text(value: str) -> str:
    """Escape user supplied text so it cannot introduce LaTeX commands."""
    return "".join(_TEXT_ESCAPE.get(char, char) for char in value)


def format_latex_url(value: str) -> str:
    """Render an HTTP(S) URL safely, preserving its usable link characters."""
    try:
        parsed = urlsplit(value.strip())
    except ValueError:
        return escape_latex_text(value)
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.netloc:
        return escape_latex_text(value)
    normalized = quote(value.strip(), safe=":/?#[]@!$&'()*+,;=%")
    return f"\\url{{{normalized}}}"


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
