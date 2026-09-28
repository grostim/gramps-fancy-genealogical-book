"""LaTeX renderer for the genealogy overview and person index."""

from urllib.parse import quote, urlsplit

from ..domain import BookModel, EditorialProfile, GenealogyPart, Note, Person


def render_latex(model: BookModel) -> str:
    family = model.reference_family
    document = [
        "\\documentclass{article}\n\\usepackage[hidelinks]{hyperref}\n"
        "\\begin{document}\n",
        f"\\section*{{{escape_latex_text(family.handle)}}}\n",
        f"{len(model.people)} people in the intermediate model.\n",
    ]

    emitted_targets: set[str] = set()
    people_by_handle = {person.handle: person for person in model.people}
    if model.genealogy is not None:
        for part in (model.genealogy.ancestry, model.genealogy.descent):
            document.append(
                _render_genealogy_part(part, people_by_handle, emitted_targets)
            )

    if model.editorial_book is not None and model.editorial_book.profiles:
        document.append("\\section*{Person profiles}\n")
        for profile in model.editorial_book.profiles:
            document.append(
                _render_profile(profile, model, people_by_handle, emitted_targets)
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
            target_id = occurrence.occurrence_id
            if target_id and target_id not in emitted_targets:
                output.append(f"\\hypertarget{{{_latex_target(target_id)}}}{{}}")
                emitted_targets.add(target_id)
            output.append(f"{escape_latex_text(name)}\n")
        output.append("\\end{itemize}\n")
    return "".join(output)


def _render_profile(
    profile: EditorialProfile,
    model: BookModel,
    people_by_handle: dict[str, Person],
    emitted_targets: set[str],
) -> str:
    person = people_by_handle.get(profile.person_handle)
    name = person.name if person is not None else ""
    name = name or profile.person_handle
    output = []
    if profile.profile_id not in emitted_targets:
        output.append(f"\\hypertarget{{{_latex_target(profile.profile_id)}}}{{}}")
        emitted_targets.add(profile.profile_id)
    output.append(f"\\subsection*{{{escape_latex_text(name)}}}\n")
    if profile.primary_occurrence_id in emitted_targets:
        output.append(
            "\\noindent See "
            f"\\hyperlink{{{_latex_target(profile.primary_occurrence_id or '')}}}"
            "{first appearance in the genealogy}.\\par\n"
        )

    if profile.event_refs:
        output.append("\\paragraph{Events}\n\\begin{itemize}\n")
        for index, reference in enumerate(profile.event_refs):
            target_id = (
                profile.event_target_ids[index]
                if index < len(profile.event_target_ids)
                else ""
            )
            anchor = _latex_anchor(target_id, emitted_targets)
            event = model.events.get(reference.event_handle)
            event_name = (
                event.description if event is not None else ""
            ) or (event.type if event is not None else "") or reference.event_handle
            details = []
            if (
                event is not None
                and event.type
                and event.type.casefold() != event_name.casefold()
            ):
                details.append(escape_latex_text(event.type))
            if event is not None and event.date is not None and event.date.display:
                details.append(escape_latex_text(event.date.display))
            if event is not None and event.place_handle:
                place = model.places.get(event.place_handle)
                place_name = (
                    (place.title or place.name) if place is not None else ""
                )
                if place_name:
                    details.append(escape_latex_text(place_name))
            if reference.role:
                details.append(escape_latex_text(reference.role))
            suffix = f" ({'; '.join(details)})" if details else ""
            output.append(
                f"\\item {anchor}{escape_latex_text(event_name)}{suffix}\n"
            )
        output.append("\\end{itemize}\n")

    notes: list[tuple[int, Note]] = []
    for index, handle in enumerate(profile.note_handles):
        note = model.notes.get(handle)
        if note is not None and note.is_publishable:
            notes.append((index, note))
    if notes:
        output.append("\\paragraph{Notes}\n")
        for index, note in notes:
            target_id = (
                profile.note_target_ids[index]
                if index < len(profile.note_target_ids)
                else ""
            )
            note_text = (
                escape_latex_text(note.text)
                if note.text
                else r"\emph{No text supplied.}"
            )
            output.append(
                f"{_latex_anchor(target_id, emitted_targets)}\\begin{{quote}}\n"
                f"{note_text}\n"
                "\\end{quote}\n"
            )
    return "".join(output)


def _latex_anchor(target_id: str, emitted_targets: set[str]) -> str:
    if not target_id or target_id in emitted_targets:
        return ""
    emitted_targets.add(target_id)
    return f"\\hypertarget{{{_latex_target(target_id)}}}{{}}"


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
