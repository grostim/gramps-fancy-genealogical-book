"""Minimal LaTeX renderer proving the shared model contract."""

from ..domain import BookModel


def render_latex(model: BookModel) -> str:
    family = model.reference_family
    return "\\documentclass{article}\n\\begin{document}\n" f"\\section*{{{family.handle}}}\n" "\\end{document}\n"

