"""LaTeX renderer for the genealogy overview and person index."""

from urllib.parse import quote, urlsplit

from ..domain import BookModel, GenealogyPart, Person


def render_latex(model: BookModel) -> str:
    family = model.reference_family
    document = [
        "\\documentclass{article}\n\\usepackage[hidelinks]{hyperref}\n"
        "\\begin{document}\n",
        f"\\section*{{{escape_latex_text(family.handle)}}}\n",
        f"{len(model.people)} people in the intermediate model.\n",
    ]

    emitted_targets: set[str] = set()
    if model.genealogy is not None:
        people_by_handle = {person.handle: person for person in model.people}
        for part in (model.genealogy.ancestry, model.genealogy.descent):
            document.append(
                _render_genealogy_part(part, people_by_handle, emitted_targets)
            )

    if model.editorial_book is not None and model.editorial_book.person_index:
        targets = {
            target.target_id: target
            for target in model.editorial_book.navigation_targets
        }
        document.append("\\section*{Person index}\n\\begin{itemize}\n")
        for entry in model.editorial_book.person_index:
            display_name = entry.display_name or entry.person_handle
            label = escape_latex_text(display_name)
            document.append(
                f"\\item \\hypertarget{{{_latex_target(entry.entry_id)}}}{{}}"
            )
            target = targets.get(entry.target_id)
            if (
                target is not None
                and target.availability == "available"
                and entry.target_id in emitted_targets
            ):
                label = (
                    f"\\hyperlink{{{_latex_target(entry.target_id)}}}"
                    f"{{{label}}}"
                )
            document.append(f"{label}\n")
        document.append("\\end{itemize}\n")

    document.append("\\end{document}\n")
    return "".join(document)


def _render_genealogy_part(
    part: GenealogyPart,
    people_by_handle: dict[str, Person],
    emitted_targets: set[str],
) -> str:
    if not part.generations:
        return ""

    output = [f"\\section*{{{escape_latex_text(part.name.title())}}}\n"]
    for generation in part.generations:
        output.append(
            f"\\subsection*{{Generation {generation.number}}}\n"
            "\\begin{itemize}\n"
        )
        for occurrence in generation.occurrences:
            person = people_by_handle.get(occurrence.person_handle)
            name = person.name if person is not None else ""
            name = name or occurrence.person_handle
            output.append("\\item ")
            target_ids = [occurrence.occurrence_id]
            if occurrence.profile_anchor:
                target_ids.append(occurrence.profile_anchor)
            for target_id in target_ids:
                if target_id and target_id not in emitted_targets:
                    output.append(
                        f"\\hypertarget{{{_latex_target(target_id)}}}{{}}"
                    )
                    emitted_targets.add(target_id)
            output.append(f"{escape_latex_text(name)}\n")
        output.append("\\end{itemize}\n")
    return "".join(output)


def _latex_target(target_id: str) -> str:
    """Map arbitrary stable model IDs to safe, deterministic hyperref labels."""
    return f"target-{target_id.encode('utf-8').hex()}"


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
