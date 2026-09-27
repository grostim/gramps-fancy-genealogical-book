"""Minimal LaTeX renderer proving the shared model contract."""

from ..domain import BookModel


def render_latex(model: BookModel) -> str:
    family = model.reference_family
    escaped = "".join(_SPECIAL.get(char, char) for char in family.handle)
    return (
        "\\documentclass{article}\n\\begin{document}\n"
        f"\\section*{{{escaped}}}\n"
        "\\end{document}\n"
    )


_SPECIAL = {
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
