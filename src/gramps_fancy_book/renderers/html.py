"""Single-document HTML renderer for the shared editorial book model."""

from __future__ import annotations

from html import escape

from ..domain import BookModel

_PART_LABELS = {
    "front_matter": "Avant-propos",
    "table_of_contents": "Sommaire",
    "ancestry": "Ascendance",
    "descent": "Descendance",
    "documentary_appendix": "Annexe documentaire",
    "person_index": "Index des personnes",
}

_NOTE_ROLE_LABELS = {
    "BOOK_DEDICATION": "Dédicace",
    "BOOK_INTRODUCTION": "Introduction",
    "BOOK_AUTHOR": "Auteur",
    "BOOK_PUBLICATION_DATE": "Date de publication",
}


def render_html(model: BookModel) -> str:
    """Render the editorial parts with stable, local navigation anchors."""
    family = model.reference_family
    people = {person.handle: person for person in model.people}
    families = dict(model.families)
    families.setdefault(family.handle, family)
    for record in families.values():
        for person in (record.father, record.mother, *record.children):
            if person is not None:
                people.setdefault(person.handle, person)

    editorial = getattr(model, "editorial_book", None)
    genealogy = getattr(model, "genealogy", None)
    title = _book_title(model, editorial)
    partner_names = [
        _person_name(person, person.handle)
        for person in (family.father, family.mother)
        if person is not None
    ]
    couple = " et ".join(partner_names)

    output = [
        "<!doctype html>\n",
        '<html lang="fr"><head><meta charset="utf-8">\n',
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n',
        f"<title>{_text(title)}</title>\n",
        "<style>\n",
        "body{font:1rem/1.6 system-ui,sans-serif;margin:0 auto;max-width:70rem;padding:1.5rem;color:#202124}\n",
        "a{color:#174ea6}a:focus-visible{outline:3px solid #174ea6;outline-offset:2px}\n",
        ".cover,.book-part{padding:1rem 0 2rem;border-bottom:1px solid #dadce0}\n",
        ".cover{text-align:center;padding:4rem 1rem}.generation{margin:1.5rem 0}\n",
        ".occurrences,.family-children,.family-partners{padding-left:1.5rem}\n",
        ".person-profile,.family-notice,.citation-entry{margin:1rem 0;padding:1rem;border-left:3px solid #9aa0a6}\n",
        ".muted{color:#5f6368}.note-text{white-space:pre-wrap}.family-links,.branch-links{font-size:.95rem}\n",
        "@media print{body{max-width:none;margin:0;padding:0}.book-part{break-before:page}a{color:inherit;text-decoration:none}}\n",
        "</style></head><body>\n",
        '<header class="cover" id="cover">\n',
        f"<h1>{_text(title)}</h1>\n",
    ]
    subtitle = _book_note_text(model, editorial, "BOOK_SUBTITLE")
    if subtitle:
        output.append(f"<p>{_text(subtitle)}</p>\n")
    if couple:
        output.append(f"<p>{_text(couple)}</p>\n")
    output.append(f'<p class="muted">Famille de référence : {_text(family.gramps_id or family.handle)}</p>\n')
    output.append("</header>\n<main>\n")

    if editorial is None:
        output.append(
            f"<p>{len(people)} personnes dans le modèle intermédiaire.</p>\n"
        )
    else:
        output.append(_render_table_of_contents(editorial.parts))
        occurrences = _occurrences_by_id(genealogy)
        sections = {
            section.section_id: section
            for section in (genealogy.family_sections if genealogy is not None else ())
        }
        profiles = {profile.person_handle: profile for profile in editorial.profiles}
        calls_by_id = {
            call.call_id: entry.entry_id
            for entry in editorial.citation_entries
            for call in entry.calls
        }
        notices = {notice.notice_id: notice for notice in editorial.family_notices}

        for part in editorial.parts:
            if part.kind in {"cover", "table_of_contents"}:
                continue
            output.append(
                _render_part(
                    part,
                    model,
                    people,
                    families,
                    occurrences,
                    sections,
                    profiles,
                    calls_by_id,
                    notices,
                )
            )
    output.append("</main>\n</body></html>\n")
    return "".join(output)


def _render_table_of_contents(parts) -> str:
    part_by_id = {part.part_id: part for part in parts}
    contents = next(
        (part for part in parts if part.kind == "table_of_contents"), None
    )
    part_ids = (
        contents.part_ids
        if contents is not None
        else tuple(part.part_id for part in parts if part.kind != "cover")
    )
    links = []
    for part_id in part_ids:
        part = part_by_id.get(part_id)
        if part is None:
            continue
        label = _PART_LABELS.get(part.kind, part.kind.replace("_", " ").capitalize())
        links.append(
            f'<li><a href="#{_attr(part.part_id)}">{_text(label)}</a></li>\n'
        )
    if not links:
        return ""
    return (
        '<nav class="book-part" id="contents" aria-label="Sommaire">\n'
        "<h2>Sommaire</h2>\n<ul>\n"
        + "".join(links)
        + "</ul>\n</nav>\n"
    )


def _render_part(
    part,
    model,
    people,
    families,
    occurrences,
    sections,
    profiles,
    calls_by_id,
    notices,
) -> str:
    label = _PART_LABELS.get(part.kind, part.kind.replace("_", " ").capitalize())
    output = [
        f'<section class="book-part" id="{_attr(part.part_id)}">\n',
        f"<h2>{_text(label)}</h2>\n",
    ]
    if part.kind == "front_matter":
        output.append(_render_front_matter(model))
    elif part.kind in {"ancestry", "descent"}:
        genealogy = getattr(model, "genealogy", None)
        genealogy_part = getattr(genealogy, part.kind, None)
        if genealogy_part is not None:
            output.append(
                _render_genealogy(
                    part.kind,
                    genealogy_part,
                    model,
                    people,
                    profiles,
                    sections,
                    calls_by_id,
                )
            )
        for notice_id in part.family_notice_ids:
            notice = notices.get(notice_id)
            if notice is not None:
                output.append(
                    _render_family_notice(
                        notice,
                        model,
                        people,
                        families,
                        occurrences,
                        sections,
                        calls_by_id,
                    )
                )
    elif part.kind == "documentary_appendix":
        entries = {entry.entry_id: entry for entry in model.editorial_book.citation_entries}
        entry_ids = part.citation_entry_ids or tuple(entries)
        for entry_id in entry_ids:
            entry = entries.get(entry_id)
            if entry is not None:
                output.append(_render_citation_entry(entry, model))
    elif part.kind == "person_index":
        entries = {entry.entry_id: entry for entry in model.editorial_book.person_index}
        entry_ids = part.person_index_entry_ids or tuple(entries)
        output.append("<ol class=\"person-index\">\n")
        for entry_id in entry_ids:
            entry = entries.get(entry_id)
            if entry is None:
                continue
            alternate = ", ".join(entry.alternate_names)
            extra = (
                f' <span class="muted">({_text(alternate)})</span>'
                if alternate
                else ""
            )
            output.append(
                f'<li id="{_attr(entry.entry_id)}"><a href="#{_attr(entry.target_id)}">'
                f"{_text(entry.display_name)}</a>{extra}</li>\n"
            )
        output.append("</ol>\n")
    output.append("</section>\n")
    return "".join(output)


def _render_front_matter(model) -> str:
    output = []
    notes = {
        item.role: model.notes.get(item.note_handle)
        for item in model.editorial_book.front_matter_notes
    }
    for role, note in notes.items():
        if note is None or role == "BOOK_TITLE" or not (note.text or "").strip():
            continue
        heading = _NOTE_ROLE_LABELS.get(role, role)
        output.append(
            f'<section><h3>{_text(heading)}</h3>'
            f'<div class="note-text">{_note_text(note.text)}</div></section>\n'
        )
    return "".join(output)


def _render_genealogy(
    part_name,
    genealogy_part,
    model,
    people,
    profiles,
    sections,
    calls_by_id,
) -> str:
    output = []
    generations = genealogy_part.generations
    root_occurrences = {
        occurrence.person_handle: occurrence
        for generation in generations
        if generation.number == 0
        for occurrence in generation.occurrences
    }
    if generations:
        output.append(
            '<nav class="generation-nav" aria-label="Navigation des générations">\n'
            "<h3>Parcourir les générations</h3>\n<ul>\n"
        )
        for generation in generations:
            target_id = _generation_id(part_name, generation.number)
            output.append(
                f'<li><a href="#{_attr(target_id)}">'
                f"Génération {generation.number}</a></li>\n"
            )
        output.append("</ul>\n</nav>\n")
    for generation in generations:
        output.append(
            f'<section class="generation" id="{_attr(_generation_id(part_name, generation.number))}">'
            f"<h3>Génération {generation.number}</h3>\n"
            '<ol class="occurrences">\n'
        )
        for occurrence in generation.occurrences:
            person = people.get(occurrence.person_handle)
            name = _person_name(person, occurrence.person_handle)
            profile = profiles.get(occurrence.person_handle)
            output.append(
                f'<li id="{_attr(occurrence.occurrence_id)}"><span>{_text(name)}</span>'
            )
            branch_links = []
            for branch_handle in getattr(occurrence, "branch_handles", ()):
                root = root_occurrences.get(branch_handle)
                if root is None or root.occurrence_id == occurrence.occurrence_id:
                    continue
                root_person = people.get(branch_handle)
                branch_links.append(
                    f'<a href="#{_attr(root.occurrence_id)}">'
                    f"{_text(_person_name(root_person, branch_handle))}</a>"
                )
            if branch_links:
                output.append(
                    ' <span class="branch-links"><span class="muted">Branche :</span> '
                    + " · ".join(branch_links)
                    + "</span>"
                )
            if profile is not None and (
                occurrence.occurrence_id == profile.primary_occurrence_id
                or occurrence.is_primary_profile
            ):
                output.append(
                    _render_profile(profile, model, calls_by_id)
                )
            else:
                target = (
                    profile.profile_id
                    if profile is not None
                    else occurrence.primary_occurrence_id
                )
                if target and target != occurrence.occurrence_id:
                    label = "Voir la fiche" if profile is not None else "Voir la première mention"
                    output.append(
                        f' <span class="muted">(<a href="#{_attr(target)}">{label}</a>)</span>'
                    )
            section_links = [
                section_id
                for section_id in occurrence.family_section_ids
                if section_id in sections
            ]
            if section_links:
                links = " · ".join(
                    f'<a href="#{_attr(section_id)}">Famille</a>'
                    for section_id in section_links
                )
                output.append(f' <span class="family-links">[{links}]</span>')
            output.append("</li>\n")
        output.append("</ol>\n</section>\n")
    return "".join(output)


def _render_profile(profile, model, calls_by_id) -> str:
    output = [f'<section class="person-profile" id="{_attr(profile.profile_id)}">']
    output.append("<h4>Notice individuelle</h4>\n")
    if profile.portrait is not None and profile.portrait.caption:
        output.append(f"<p>{_text(profile.portrait.caption)}</p>\n")
    output.append(_render_events(profile.event_refs, profile.event_target_ids, model))
    for handle, target in zip(profile.note_handles, profile.note_target_ids):
        note = model.notes.get(handle)
        if note is not None:
            output.append(
                f'<div id="{_attr(target)}" class="note-text">{_note_text(note.text or "")}</div>\n'
            )
    citations = [
        calls_by_id[call_id]
        for call_id in profile.citation_call_ids
        if call_id in calls_by_id
    ]
    if citations:
        output.append("<p>Références : ")
        output.append(
            ", ".join(
                f'<a href="#{_attr(entry_id)}">{_text(entry_id)}</a>'
                for entry_id in dict.fromkeys(citations)
            )
        )
        output.append("</p>\n")
    output.append("</section>\n")
    return "".join(output)


def _render_family_notice(
    notice,
    model,
    people,
    families,
    occurrences,
    sections,
    calls_by_id,
) -> str:
    family = families.get(notice.family_handle)
    family_label = (
        family.gramps_id or family.handle if family is not None else notice.family_handle
    )
    output = [
        f'<article class="family-notice" id="{_attr(notice.notice_id)}">\n',
        f"<h3>Famille {_text(family_label)}</h3>\n",
    ]
    for section_id in notice.family_section_ids:
        section = sections.get(section_id)
        if section is None:
            continue
        output.append(
            f'<section id="{_attr(section.section_id)}"><h4>Section familiale</h4>\n'
        )
        if section.partner_occurrence_ids:
            output.append("<h5>Partenaires</h5><ul class=\"family-partners\">\n")
            for occurrence_id in section.partner_occurrence_ids:
                occurrence = occurrences.get(occurrence_id)
                if occurrence is None:
                    continue
                person = people.get(occurrence.person_handle)
                output.append(
                    f'<li><a href="#{_attr(occurrence_id)}">'
                    f"{_text(_person_name(person, occurrence.person_handle))}</a></li>\n"
                )
            output.append("</ul>\n")
        if section.child_occurrence_ids:
            output.append("<h5>Enfants et filiations</h5><ul class=\"family-children\">\n")
            links_by_child = {}
            for link in section.parent_child_links:
                links_by_child.setdefault(link.child_occurrence_id, []).append(link)
            for occurrence_id in section.child_occurrence_ids:
                occurrence = occurrences.get(occurrence_id)
                if occurrence is None:
                    continue
                person = people.get(occurrence.person_handle)
                output.append(
                    f'<li><a href="#{_attr(occurrence_id)}">'
                    f"{_text(_person_name(person, occurrence.person_handle))}</a>"
                )
                relation_labels = list(
                    dict.fromkeys(
                        str(link.relationship_type)
                        for link in links_by_child.get(occurrence_id, ())
                        if link.relationship_type not in (None, "")
                    )
                )
                if relation_labels:
                    output.append(
                        f' <span class="muted">— filiation : {_text(", ".join(relation_labels))}</span>'
                    )
                output.append("</li>\n")
            output.append("</ul>\n")
        output.append("</section>\n")
    output.append(_render_events(notice.event_refs, notice.event_target_ids, model))
    for handle, target in zip(notice.note_handles, notice.note_target_ids):
        note = model.notes.get(handle)
        if note is not None:
            output.append(
                f'<div id="{_attr(target)}" class="note-text">{_note_text(note.text or "")}</div>\n'
            )
    citations = [
        calls_by_id[call_id]
        for call_id in notice.citation_call_ids
        if call_id in calls_by_id
    ]
    if citations:
        output.append("<p>Références : ")
        output.append(
            ", ".join(
                f'<a href="#{_attr(entry_id)}">{_text(entry_id)}</a>'
                for entry_id in dict.fromkeys(citations)
            )
        )
        output.append("</p>\n")
    output.append("</article>\n")
    return "".join(output)


def _render_events(references, target_ids, model) -> str:
    if not references:
        return ""
    output = ["<ul>\n"]
    for index, reference in enumerate(references):
        event = model.events.get(reference.event_handle)
        details = []
        if event is not None:
            if event.date is not None and event.date.display:
                details.append(event.date.display)
            if event.description:
                details.append(event.description)
            if event.place_handle:
                place = model.places.get(event.place_handle)
                place_name = (
                    (place.title or place.name)
                    if place is not None
                    else event.place_handle
                )
                if place_name:
                    details.append(place_name)
        event_label = event.type if event is not None else reference.event_handle
        target = target_ids[index] if index < len(target_ids) else ""
        id_attr = f' id="{_attr(target)}"' if target else ""
        summary = " — ".join(details)
        output.append(
            f"<li{id_attr}><strong>{_text(event_label)}</strong>"
            f"{' — ' + _text(summary) if summary else ''}</li>\n"
        )
    output.append("</ul>\n")
    return "".join(output)


def _render_citation_entry(entry, model) -> str:
    citation = model.citations.get(entry.citation_handle)
    source = model.sources.get(entry.source_handle) if entry.source_handle else None
    title = source.title if source is not None and source.title else entry.citation_handle
    output = [
        f'<article class="citation-entry" id="{_attr(entry.entry_id)}">\n',
        f"<h3>{_text(title)}</h3>\n",
    ]
    details = []
    if citation is not None:
        if citation.page:
            details.append(citation.page)
        if citation.date is not None and citation.date.display:
            details.append(citation.date.display)
    if source is not None:
        details.extend(item for item in (source.author, source.publication_info) if item)
    if details:
        output.append(f"<p>{_text(' — '.join(details))}</p>\n")
    for reference in entry.repository_refs:
        repository = model.repositories.get(reference.repository_handle)
        repository_name = repository.name if repository is not None else reference.repository_handle
        call_number = reference.call_number
        output.append(
            f"<p>{_text(repository_name)}"
            f"{': ' + _text(call_number) if call_number else ''}</p>\n"
        )
    if entry.calls:
        output.append("<ul>\n")
        for call in entry.calls:
            output.append(
                f'<li><a href="#{_attr(call.context_id)}">{_text(call.owner_type)} '
                f"{_text(call.owner_handle)}</a></li>\n"
            )
        output.append("</ul>\n")
    output.append("</article>\n")
    return "".join(output)


def _book_title(model, editorial) -> str:
    title = _book_note_text(model, editorial, "BOOK_TITLE")
    return title or "Livre généalogique"


def _book_note_text(model, editorial, role) -> str:
    if editorial is None:
        return ""
    for item in editorial.front_matter_notes:
        if item.role == role:
            note = model.notes.get(item.note_handle)
            if note is not None and note.text:
                return note.text.strip()
    return ""


def _occurrences_by_id(genealogy):
    if genealogy is None:
        return {}
    return {
        occurrence.occurrence_id: occurrence
        for part in (genealogy.ancestry, genealogy.descent)
        for generation in part.generations
        for occurrence in generation.occurrences
    }


def _generation_id(part_name: str, generation_number: int) -> str:
    return f"generation:{part_name}:{generation_number}"


def _person_name(person, fallback: str) -> str:
    return str(person.name) if person is not None and person.name else fallback


def _note_text(value: str) -> str:
    return _text(value)


def _text(value) -> str:
    return escape("" if value is None else str(value), quote=False)


def _attr(value) -> str:
    return escape("" if value is None else str(value), quote=True)
