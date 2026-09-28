"""LaTeX renderer for the genealogy overview and person index."""

from pathlib import PurePosixPath
from urllib.parse import quote, urlsplit

from ..domain import (
    BookModel,
    EditorialCitationCall,
    EditorialCitationEntry,
    EditorialMediaArtifact,
    EditorialPortrait,
    EditorialProfile,
    GenealogyPart,
    MediaReference,
    Note,
    Person,
    RepositoryReference,
    Url,
)


def render_latex(model: BookModel) -> str:
    family = model.reference_family
    document = [
        "\\documentclass{article}\n"
        "\\usepackage[hidelinks]{hyperref}\n\\usepackage{graphicx}\n"
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
        citation_by_call = {
            call.call_id: entry
            for entry in model.editorial_book.citation_entries
            for call in entry.calls
        }
        for profile in model.editorial_book.profiles:
            document.append(
                _render_profile(
                    profile,
                    model,
                    people_by_handle,
                    emitted_targets,
                    citation_by_call,
                )
            )

    if model.editorial_book is not None and model.editorial_book.citation_entries:
        document.append(
            _render_citation_appendix(
                model.editorial_book.citation_entries, model, emitted_targets
            )
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
    citation_by_call: dict[str, EditorialCitationEntry],
) -> str:
    person = people_by_handle.get(profile.person_handle)
    name = person.name if person is not None else ""
    name = name or profile.person_handle
    output = []
    if profile.profile_id not in emitted_targets:
        output.append(f"\\hypertarget{{{_latex_target(profile.profile_id)}}}{{}}")
        emitted_targets.add(profile.profile_id)
    output.append(f"\\subsection*{{{escape_latex_text(name)}}}\n")
    if profile.portrait is not None:
        output.append(
            _render_media_image(
                profile.portrait,
                profile.portrait.caption,
                model.media_artifacts,
                width="0.75\\linewidth",
            )
        )
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

    citation_entries = {
        citation_by_call[call_id].entry_id: citation_by_call[call_id]
        for call_id in profile.citation_call_ids
        if call_id in citation_by_call
    }
    if citation_entries:
        output.append("\\paragraph{Sources}\n\\begin{itemize}\n")
        for entry in citation_entries.values():
            label = _citation_title(entry, model)
            output.append(
                f"\\item \\hyperlink{{{_latex_target(entry.entry_id)}}}"
                f"{{{escape_latex_text(label)}}}\n"
            )
        output.append("\\end{itemize}\n")
    return "".join(output)


def _render_citation_appendix(
    entries: tuple[EditorialCitationEntry, ...],
    model: BookModel,
    emitted_targets: set[str],
) -> str:
    output = ["\\section*{Documentary appendix}\n\\begin{itemize}\n"]
    profiles = {
        profile.profile_id: profile
        for profile in (model.editorial_book.profiles if model.editorial_book else ())
    }
    people_by_handle = {person.handle: person for person in model.people}
    for entry in entries:
        citation = model.citations.get(entry.citation_handle)
        source_handle = entry.source_handle or (
            citation.source_handle if citation is not None else None
        )
        source = model.sources.get(source_handle) if source_handle else None
        output.append(
            f"\\item {_latex_anchor(entry.entry_id, emitted_targets)}"
            f"\\textbf{{{escape_latex_text(_citation_title(entry, model))}}}\n"
        )
        details = []
        if source is not None and source.author:
            details.append(escape_latex_text(source.author))
        if source is not None and source.publication_info:
            details.append(escape_latex_text(source.publication_info))
        if citation is not None and citation.page:
            details.append(f"p. {escape_latex_text(citation.page)}")
        if citation is not None and citation.date is not None and citation.date.display:
            details.append(escape_latex_text(citation.date.display))
        if details:
            output.append(f"\\par {'; '.join(details)}\n")

        urls: list[Url] = []
        if citation is not None:
            urls.extend(citation.urls)
        if source is not None:
            urls.extend(source.urls)
        repositories = []
        for reference in entry.repository_refs:
            repository = model.repositories.get(reference.repository_handle)
            repository_name = (
                (repository.name or repository.gramps_id)
                if repository is not None
                else ""
            ) or reference.repository_handle
            repositories.append((repository_name, reference))
            if repository is not None:
                urls.extend(repository.urls)
        if repositories:
            output.append("\\par Repositories: ")
            output.append(
                "; ".join(
                    _format_repository(repository_name, reference)
                    for repository_name, reference in repositories
                )
            )
            output.append("\n")

        if urls:
            output.append("\\par URLs: ")
            output.append("; ".join(_format_url(item) for item in _unique_urls(urls)))
            output.append("\n")

        media_labels = []
        for reference in entry.media_refs:
            media = model.media.get(reference.media_handle)
            media_labels.append(
                (media.description or media.gramps_id if media else "")
                or reference.media_handle
            )
        if media_labels:
            output.append(
                "\\par Media: "
                + "; ".join(escape_latex_text(label) for label in media_labels)
                + "\n"
            )
        for reference in entry.media_refs:
            media = model.media.get(reference.media_handle)
            caption = media.description if media is not None else ""
            output.append(
                _render_media_image(
                    reference,
                    caption,
                    model.media_artifacts,
                    width="0.6\\linewidth",
                )
            )

        call_labels = [
            (call, _citation_call_label(call, profiles, people_by_handle, model))
            for call in entry.calls
        ]
        if call_labels:
            output.append("\\begin{itemize}\n")
            for call, label in call_labels:
                context = profiles.get(call.context_id)
                linked_label = escape_latex_text(label)
                if context is not None and context.profile_id in emitted_targets:
                    linked_label = (
                        f"\\hyperlink{{{_latex_target(context.profile_id)}}}"
                        f"{{{linked_label}}}"
                    )
                output.append(
                    f"\\item {_latex_anchor(call.call_id, emitted_targets)}"
                    f"{linked_label}\n"
                )
            output.append("\\end{itemize}\n")
    output.append("\\end{itemize}\n")
    return "".join(output)


def _citation_title(entry: EditorialCitationEntry, model: BookModel) -> str:
    citation = model.citations.get(entry.citation_handle)
    source_handle = entry.source_handle or (
        citation.source_handle if citation is not None else None
    )
    source = model.sources.get(source_handle) if source_handle else None
    if source is not None:
        title = source.title or source.abbreviation
        if title:
            return title
    if citation is not None and citation.gramps_id:
        return citation.gramps_id
    return entry.citation_handle


def _format_repository(
    repository_name: str, reference: RepositoryReference
) -> str:
    details = [escape_latex_text(repository_name)]
    if reference.call_number:
        details.append(escape_latex_text(reference.call_number))
    if reference.media_type:
        details.append(escape_latex_text(reference.media_type))
    return ", ".join(details)


def _format_url(url: Url) -> str:
    rendered = format_latex_url(url.path)
    if url.description:
        return f"{rendered} ({escape_latex_text(url.description)})"
    return rendered


def _citation_call_label(
    call: EditorialCitationCall,
    profiles: dict[str, EditorialProfile],
    people_by_handle: dict[str, Person],
    model: BookModel,
) -> str:
    profile = profiles.get(call.context_id)
    person = people_by_handle.get(profile.person_handle) if profile is not None else None
    context_name = person.name if person is not None else ""
    if call.owner_type == "event":
        event = model.events.get(call.owner_handle)
        owner_name = (
            (event.description or event.type or event.gramps_id)
            if event is not None
            else ""
        )
    elif call.owner_type == "media":
        media = model.media.get(call.owner_handle)
        owner_name = (
            (media.description or media.gramps_id) if media is not None else ""
        )
    elif call.owner_type == "note":
        note = model.notes.get(call.owner_handle)
        owner_name = (note.gramps_id or "Note") if note is not None else ""
    else:
        owner_name = person.name if call.owner_type == "person" and person else ""
    owner_name = owner_name or call.owner_handle
    if context_name:
        return f"{context_name} — {call.owner_type}: {owner_name}"
    return f"{call.owner_type}: {owner_name}"


def _unique_urls(urls: list[Url]) -> tuple[Url, ...]:
    seen = set()
    unique = []
    for url in urls:
        if url.path not in seen:
            unique.append(url)
            seen.add(url.path)
    return tuple(unique)


def _render_media_image(
    reference: EditorialPortrait | MediaReference,
    caption: str,
    artifacts: list[EditorialMediaArtifact],
    *,
    width: str,
) -> str:
    media_ref = reference.media_ref if isinstance(reference, EditorialPortrait) else reference
    artifact = next(
        (
            item
            for item in artifacts
            if item.media_handle == media_ref.media_handle
            and item.rectangle == media_ref.rectangle
            and item.action == "reproduce"
        ),
        None,
    )
    if artifact is None or artifact.asset_path is None:
        return ""
    path = _safe_latex_media_path(artifact.asset_path, artifact.cache_key)
    if path is None:
        return ""
    output = [
        "\\begin{center}\n"
        f"\\includegraphics[width={width}]{{\\detokenize{{{path}}}}}\n"
    ]
    if caption:
        output.append(f"{{\\small {escape_latex_text(caption)}}}\n")
    output.append("\\end{center}\n")
    return "".join(output)


def _safe_latex_media_path(asset_path: str, cache_key: str | None) -> str | None:
    if (
        cache_key is None
        or len(cache_key) != 64
        or any(char not in "0123456789abcdef" for char in cache_key)
    ):
        return None
    parts = PurePosixPath(asset_path)
    if (
        parts.is_absolute()
        or len(parts.parts) != 2
        or parts.parts[0] in {".", ".."}
        or parts.parts[1] != f"{cache_key}.png"
        or any(char in asset_path for char in "\\{}%#\n\r\0")
    ):
        return None
    return asset_path


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
