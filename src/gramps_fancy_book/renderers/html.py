"""Single-document HTML renderer for the shared editorial book model."""

from __future__ import annotations

from html import escape
from pathlib import PurePosixPath

from ..book_language import model_book_language
from ..domain import BookModel
from .citation_numbers import citation_number_map
from .html_notes import (
    render_html_inline_note,
    render_html_inline_text,
    render_html_note,
    safe_html_url,
)
from .labels import gramps_type_label, label, owner_label

_FRONT_MATTER_COVER_ROLES = {
    "BOOK_TITLE",
    "BOOK_SUBTITLE",
    "BOOK_AUTHOR",
    "BOOK_PUBLICATION_DATE",
}


def render_html(
    model: BookModel,
    *,
    include_media: bool = False,
    gramps_type_labels: dict[tuple[str, str], str] | None = None,
) -> str:
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
    media_context = _media_context(model, include_media)
    language = model_book_language(model)
    title = _book_title(model, editorial)
    partner_names = [
        _person_name(person, person.handle)
        for person in (family.father, family.mother)
        if person is not None
    ]
    couple = label(model, "and").join(partner_names)

    output = [
        "<!doctype html>\n",
        f'<html lang="{language}"><head><meta charset="utf-8">\n',
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n',
        f"<title>{_text(title)}</title>\n",
        "<style>\n",
        "body{font:1rem/1.6 system-ui,sans-serif;margin:0 auto;max-width:70rem;padding:clamp(.75rem,3vw,1.5rem);color:#202124;overflow-wrap:anywhere}\n",
        "a{color:#174ea6}:focus-visible{outline:3px solid #174ea6;outline-offset:2px}\n",
        ".skip-link{position:absolute;left:.75rem;top:-5rem;background:#fff;color:#174ea6;padding:.5rem .75rem;border:2px solid #174ea6;z-index:10}.skip-link:focus-visible{top:.75rem}\n",
        "h1{font-size:clamp(1.75rem,6vw,3rem);line-height:1.15}\n",
        ".cover,.book-part{padding:1rem 0 2rem;border-bottom:1px solid #dadce0}\n",
        ".cover{text-align:center;padding:4rem 1rem}.generation{margin:1.5rem 0}\n",
        ".occurrences,.family-children,.family-partners{padding-left:1.5rem}\n",
        ".person-profile,.family-notice,.citation-entry{margin:1rem 0;padding:1rem;border-left:3px solid #9aa0a6}\n",
        ".cover-portraits{display:flex;justify-content:center;gap:1rem;flex-wrap:wrap}.media-item{margin:1rem auto;text-align:center}.media-item img{display:block;max-width:100%;height:auto;margin:auto}.featured-media img{max-height:80vh;object-fit:contain}.media-reference{padding:.5rem 0}\n",
        ".citation-number{font-variant-numeric:tabular-nums;white-space:nowrap}.citation-references a{white-space:nowrap}\n",
        ".muted{color:#5f6368}.note-text{white-space:normal}.note-text p:first-child{margin-top:0}.note-text p:last-child{margin-bottom:0}.note-text pre{white-space:pre-wrap;overflow-wrap:anywhere}.family-links,.branch-links{font-size:.95rem}\n",
        "@media(max-width:40rem){.cover{padding:2.5rem .5rem 1.5rem}.generation{margin:1rem 0}.occurrences,.family-children,.family-partners{padding-left:1rem}.person-profile,.family-notice,.citation-entry{padding:.75rem}}\n",
        "@media print{body{max-width:none;margin:0;padding:0}.book-part{break-before:page}a{color:inherit;text-decoration:none}}\n",
        "</style></head><body>\n",
        f'<a class="skip-link" href="#main-content">{_text(label(model, "skip_to_content"))}</a>\n',
        '<header class="cover" id="cover">\n',
        f"<h1>{_render_cover_note(model, editorial, 'BOOK_TITLE') or _text(title)}</h1>\n",
    ]
    subtitle = _render_cover_note(model, editorial, "BOOK_SUBTITLE")
    if subtitle:
        output.append(f"<p>{subtitle}</p>\n")
    for role, role_label in (
        ("BOOK_AUTHOR", label(model, "author")),
        ("BOOK_PUBLICATION_DATE", label(model, "publication_date")),
    ):
        cover_note = _render_cover_note(model, editorial, role)
        if cover_note:
            output.append(
                f'<p><span class="muted">{_text(role_label)} : </span>{cover_note}</p>\n'
            )
    if couple:
        output.append(f"<p>{_text(couple)}</p>\n")
    output.append(_render_cover_portraits(model, people, media_context))
    output.append(
        f'<p class="muted">{_text(label(model, "reference_family"))} : '
        f'{_text(family.gramps_id or family.handle)}</p>\n'
    )
    output.append("</header>\n<main id=\"main-content\" tabindex=\"-1\">\n")

    if editorial is None:
        output.append(
            f"<p>{len(people)} {_text(label(model, 'intermediate_model'))}</p>\n"
        )
    else:
        output.append(_render_table_of_contents(editorial.parts, model))
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
        citation_numbers = citation_number_map(
            editorial, context_order=_citation_context_order(model, editorial)
        )
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
                    citation_numbers,
                    notices,
                    media_context,
                    gramps_type_labels,
                )
            )
    output.append("</main>\n</body></html>\n")
    return "".join(output)


def _citation_context_order(model, editorial) -> tuple[str, ...]:
    """Return profile and family-notice IDs in the HTML book's display order."""
    profiles = {profile.person_handle: profile for profile in editorial.profiles}
    notices = {notice.notice_id for notice in editorial.family_notices}
    genealogy = getattr(model, "genealogy", None)
    context_ids = []
    seen = set()
    for part in editorial.parts:
        if part.kind not in {"ancestry", "descent"}:
            continue
        genealogy_part = getattr(genealogy, part.kind, None)
        if genealogy_part is not None:
            for generation in genealogy_part.generations:
                for occurrence in generation.occurrences:
                    profile = profiles.get(occurrence.person_handle)
                    if profile is None or not (
                        occurrence.occurrence_id == profile.primary_occurrence_id
                        or getattr(occurrence, "is_primary_profile", False)
                    ):
                        continue
                    if profile.profile_id not in seen:
                        context_ids.append(profile.profile_id)
                        seen.add(profile.profile_id)
        for notice_id in part.family_notice_ids:
            if notice_id in notices and notice_id not in seen:
                context_ids.append(notice_id)
                seen.add(notice_id)
    return tuple(context_ids)


def _render_table_of_contents(parts, model) -> str:
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
        if part.kind == "front_matter" and not _has_front_matter_content(model):
            continue
        part_label = _part_label(model, part.kind)
        links.append(
            f'<li><a href="#{_attr(part.part_id)}">{_text(part_label)}</a></li>\n'
        )
    if not links:
        return ""
    return (
        f'<nav class="book-part" id="contents" aria-label="{_attr(label(model, "contents"))}">\n'
        f"<h2>{_text(label(model, 'contents'))}</h2>\n<ul>\n"
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
    citation_numbers,
    notices,
    media_context,
    gramps_type_labels=None,
) -> str:
    if part.kind == "front_matter" and not _has_front_matter_content(model):
        return ""
    part_label = _part_label(model, part.kind)
    output = [
        f'<section class="book-part" id="{_attr(part.part_id)}">\n',
        f"<h2>{_text(part_label)}</h2>\n",
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
                    citation_numbers,
                    media_context,
                    gramps_type_labels,
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
                        citation_numbers,
                        media_context,
                        gramps_type_labels,
                    )
                )
    elif part.kind == "documentary_appendix":
        entries = {entry.entry_id: entry for entry in model.editorial_book.citation_entries}
        entry_ids = part.citation_entry_ids or tuple(entries)
        entry_ids = sorted(
            entry_ids,
            key=lambda entry_id: citation_numbers.get(entry_id, float("inf")),
        )
        for entry_id in entry_ids:
            entry = entries.get(entry_id)
            if entry is not None:
                output.append(
                    _render_citation_entry(
                        entry,
                        model,
                        media_context,
                        citation_numbers,
                        gramps_type_labels,
                    )
                )
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


def _part_label(model, kind: str) -> str:
    if kind == "table_of_contents":
        return label(model, "contents")
    if kind in {
        "front_matter",
        "ancestry",
        "descent",
        "documentary_appendix",
        "person_index",
    }:
        return label(model, kind)
    return kind.replace("_", " ").capitalize()


def _render_front_matter(model) -> str:
    output = []
    notes = {
        item.role: model.notes.get(item.note_handle)
        for item in model.editorial_book.front_matter_notes
    }
    for role, note in notes.items():
        if (
            note is None
            or role in _FRONT_MATTER_COVER_ROLES
            or not (note.text or "").strip()
        ):
            continue
        heading = {
            "BOOK_DEDICATION": label(model, "dedication"),
            "BOOK_INTRODUCTION": label(model, "introduction"),
            "BOOK_AUTHOR": label(model, "author"),
            "BOOK_PUBLICATION_DATE": label(model, "publication_date"),
        }.get(role, role)
        output.append(
            f'<section><h3>{_text(heading)}</h3>'
            f'<div class="note-text">{render_html_note(note)}</div></section>\n'
        )
    return "".join(output)


def _has_front_matter_content(model) -> bool:
    editorial = getattr(model, "editorial_book", None)
    if editorial is None:
        return False
    notes = getattr(editorial, "front_matter_notes", ())
    model_notes = getattr(model, "notes", {}) or {}
    return any(
        item.role not in _FRONT_MATTER_COVER_ROLES
        and (note := model_notes.get(item.note_handle)) is not None
        and bool((note.text or "").strip())
        for item in notes
    )


def _render_genealogy(
    part_name,
    genealogy_part,
    model,
    people,
    profiles,
    sections,
    calls_by_id,
    citation_numbers,
    media_context,
    gramps_type_labels=None,
) -> str:
    output = []
    generations = genealogy_part.generations
    root_occurrences = {
        occurrence.person_handle: occurrence
        for generation in generations
        if generation.number == 0
        for occurrence in generation.occurrences
        if getattr(occurrence, "roles", None) is None
        or "central" in occurrence.roles
    }
    if generations:
        output.append(
            f'<nav class="generation-nav" aria-label="{_attr(label(model, "generation_navigation"))}">\n'
            f"<h3>{_text(label(model, 'browse_generations'))}</h3>\n<ul>\n"
        )
        for generation in generations:
            target_id = _generation_id(part_name, generation.number)
            output.append(
                f'<li><a href="#{_attr(target_id)}">'
                f"{_text(label(model, 'generation'))} {generation.number}</a></li>\n"
            )
        output.append("</ul>\n</nav>\n")
    for generation in generations:
        output.append(
            f'<section class="generation" id="{_attr(_generation_id(part_name, generation.number))}">'
            f"<h3>{_text(label(model, 'generation'))} {generation.number}</h3>\n"
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
                    f' <span class="branch-links"><span class="muted">{_text(label(model, "branch"))} :</span> '
                    + " · ".join(branch_links)
                    + "</span>"
                )
            if profile is not None and (
                occurrence.occurrence_id == profile.primary_occurrence_id
                or occurrence.is_primary_profile
            ):
                output.append(
                    _render_profile(
                        profile,
                        model,
                        calls_by_id,
                        citation_numbers,
                        media_context,
                        gramps_type_labels,
                    )
                )
            else:
                target = (
                    profile.profile_id
                    if profile is not None
                    else occurrence.primary_occurrence_id
                )
                if target and target != occurrence.occurrence_id:
                    link_label = label(
                        model,
                        "view_profile" if profile is not None else "view_first_mention",
                    )
                    output.append(
                        f' <span class="muted">(<a href="#{_attr(target)}">{_text(link_label)}</a>)</span>'
                    )
            section_links = [
                section_id
                for section_id in occurrence.family_section_ids
                if section_id in sections
            ]
            if section_links:
                links = " · ".join(
                    f'<a href="#{_attr(section_id)}">{_text(label(model, "family"))}</a>'
                    for section_id in section_links
                )
                output.append(f' <span class="family-links">[{links}]</span>')
            output.append("</li>\n")
        output.append("</ol>\n</section>\n")
    return "".join(output)


def _render_profile(
    profile,
    model,
    calls_by_id,
    citation_numbers,
    media_context,
    gramps_type_labels=None,
) -> str:
    output = [f'<section class="person-profile" id="{_attr(profile.profile_id)}">']
    output.append(f"<h4>{_text(label(model, 'individual_profile'))}</h4>\n")
    if (
        profile.portrait is not None
        and profile.portrait.caption
        and not media_context["enabled"]
    ):
        output.append(f"<p>{_text(profile.portrait.caption)}</p>\n")
    if profile.portrait is not None:
        output.append(
            _render_media_reference(
                profile.portrait.media_ref,
                profile.portrait.caption,
                model,
                media_context,
                context_type="portrait",
                context_id=profile.profile_id,
                alt=(
                    profile.portrait.caption.strip()
                    or _portrait_alt(profile.person_handle, model)
                ),
            )
        )
        placement = media_context["placements"].get(
            profile.portrait.media_ref.media_handle
        )
        if placement is not None and placement.is_featured:
            output.append(
                _render_media_reference(
                    profile.portrait.media_ref,
                    placement.caption or profile.portrait.caption,
                    model,
                    media_context,
                    context_type="profile",
                    context_id=profile.profile_id,
                )
            )
    portrait_ref = (
        profile.portrait.media_ref
        if profile.portrait is not None
        else None
    )
    for reference in getattr(profile, "media_refs", ()):
        if portrait_ref is not None and reference == portrait_ref:
            continue
        media = model.media.get(reference.media_handle)
        output.append(
            _render_media_reference(
                reference,
                media.description if media is not None else "",
                model,
                media_context,
                context_type="profile",
                context_id=profile.profile_id,
            )
        )
    output.append(
        _render_events(
            profile.event_refs, profile.event_target_ids, model, gramps_type_labels
        )
    )
    for handle, target in zip(profile.note_handles, profile.note_target_ids):
        note = model.notes.get(handle)
        if note is not None:
            output.append(
                f'<div id="{_attr(target)}" class="note-text">{render_html_note(note)}</div>\n'
            )
    output.append(
        _render_citation_references(
            profile.citation_call_ids, calls_by_id, citation_numbers, model
        )
    )
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
    citation_numbers,
    media_context,
    gramps_type_labels=None,
) -> str:
    family = families.get(notice.family_handle)
    family_label = (
        family.gramps_id or family.handle if family is not None else notice.family_handle
    )
    output = [
        f'<article class="family-notice" id="{_attr(notice.notice_id)}">\n',
        f"<h3>{_text(label(model, 'family'))} {_text(family_label)}</h3>\n",
    ]
    for section_id in notice.family_section_ids:
        section = sections.get(section_id)
        if section is None:
            continue
        output.append(
            f'<section id="{_attr(section.section_id)}"><h4>{_text(label(model, "family_section"))}</h4>\n'
        )
        if section.partner_occurrence_ids:
            output.append(f"<h5>{_text(label(model, 'partners'))}</h5><ul class=\"family-partners\">\n")
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
            output.append(f"<h5>{_text(label(model, 'children_and_parentage'))}</h5><ul class=\"family-children\">\n")
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
                relation_labels = []
                for link in links_by_child.get(occurrence_id, ()):
                    if link.relationship_type in (None, ""):
                        continue
                    parent = occurrences.get(link.parent_occurrence_id)
                    if parent is None:
                        continue
                    parent_person = people.get(parent.person_handle)
                    relationship_type = gramps_type_label(
                        "child_relationship",
                        link.relationship_type,
                        gramps_type_labels,
                    )
                    relation = (
                        f"{_person_name(parent_person, parent.person_handle)} : "
                        f"{relationship_type}"
                    )
                    if relation not in relation_labels:
                        relation_labels.append(relation)
                if relation_labels:
                    relation_text = _text(" ; ".join(relation_labels))
                    output.append(
                        f' <span class="muted">— {_text(label(model, "filiation"))} : {relation_text}</span>'
                    )
                output.append("</li>\n")
            output.append("</ul>\n")
        output.append("</section>\n")
    for reference in getattr(notice, "media_refs", ()):
        media = model.media.get(reference.media_handle)
        output.append(
            _render_media_reference(
                reference,
                media.description if media is not None else "",
                model,
                media_context,
                context_type="family_notice",
                context_id=notice.notice_id,
            )
        )
    output.append(
        _render_events(
            notice.event_refs, notice.event_target_ids, model, gramps_type_labels
        )
    )
    for handle, target in zip(notice.note_handles, notice.note_target_ids):
        note = model.notes.get(handle)
        if note is not None:
            output.append(
                f'<div id="{_attr(target)}" class="note-text">{render_html_note(note)}</div>\n'
            )
    output.append(
        _render_citation_references(
            notice.citation_call_ids, calls_by_id, citation_numbers, model
        )
    )
    output.append("</article>\n")
    return "".join(output)


def _render_events(references, target_ids, model, gramps_type_labels=None) -> str:
    if not references:
        return ""
    output = ["<ul>\n"]
    for index, reference in enumerate(references):
        event = model.events.get(reference.event_handle)
        details = []
        if reference.role:
            details.append(
                f"{label(model, 'role')} : "
                f"{gramps_type_label('event_role', reference.role, gramps_type_labels)}"
            )
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
        event_label = (
            gramps_type_label("event", event.type, gramps_type_labels)
            if event is not None
            else reference.event_handle
        )
        target = target_ids[index] if index < len(target_ids) else ""
        id_attr = f' id="{_attr(target)}"' if target else ""
        summary = " — ".join(details)
        output.append(
            f"<li{id_attr}><strong>{_text(event_label)}</strong>"
            f"{' — ' + _text(summary) if summary else ''}</li>\n"
        )
    output.append("</ul>\n")
    return "".join(output)


def _render_citation_references(call_ids, calls_by_id, citation_numbers, model) -> str:
    entry_ids = tuple(
        dict.fromkeys(
            calls_by_id[call_id] for call_id in call_ids if call_id in calls_by_id
        )
    )
    if not entry_ids:
        return ""
    links = []
    for entry_id in entry_ids:
        number = citation_numbers.get(entry_id)
        if number is not None:
            links.append(
                f'<a href="#{_attr(entry_id)}">'
                f'<span class="citation-number">[{number}]</span></a>'
            )
    if not links:
        return ""
    return (
        f'<p class="citation-references">{_text(label(model, "references"))} : '
        + ", ".join(links)
        + "</p>\n"
    )


def _render_citation_entry(
    entry, model, media_context, citation_numbers, gramps_type_labels=None
) -> str:
    citation = model.citations.get(entry.citation_handle)
    source = model.sources.get(entry.source_handle) if entry.source_handle else None
    title = source.title if source is not None and source.title else entry.citation_handle
    number = citation_numbers.get(entry.entry_id)
    number_label = f"[{number}] " if number is not None else ""
    output = [
        f'<article class="citation-entry" id="{_attr(entry.entry_id)}">\n',
        f'<h3><span class="citation-number">{_text(number_label)}</span>'
        f"{_text(title)}</h3>\n",
    ]
    identifiers = []
    if citation is not None and citation.gramps_id:
        identifiers.append(f"{_text(label(model, 'citation'))} {_text(citation.gramps_id)}")
    if source is not None and source.gramps_id:
        identifiers.append(f"{_text(label(model, 'source'))} {_text(source.gramps_id)}")
    if identifiers:
        output.append(
            f'<p class="muted">{_text(label(model, "gramps_identifiers"))} : '
            + " · ".join(identifiers)
            + "</p>\n"
        )
    details = []
    if citation is not None:
        if citation.page:
            details.append(citation.page)
        if citation.date is not None and citation.date.display:
            details.append(citation.date.display)
    if source is not None:
        details.extend(
            item
            for item in (
                source.author,
                source.publication_info,
                source.abbreviation,
            )
            if item
        )
    if details:
        output.append(f"<p>{_text(' — '.join(details))}</p>\n")
    for reference in entry.repository_refs:
        repository = model.repositories.get(reference.repository_handle)
        repository_name = repository.name if repository is not None else reference.repository_handle
        repository_details = [repository_name]
        if repository is not None and repository.type:
            repository_details.append(repository.type)
        call_number = reference.call_number
        if call_number:
            repository_details.append(call_number)
        output.append(f"<p>{_text(' — '.join(repository_details))}</p>\n")
    for target, description in _citation_urls(entry, model):
        link = _render_html_url(target, description, class_name="citation-url")
        output.append(f"<p>{link}</p>\n")
    for reference in getattr(entry, "media_refs", ()):
        media = model.media.get(reference.media_handle)
        output.append(
            _render_media_reference(
                reference,
                media.description if media is not None else "",
                model,
                media_context,
                context_type="citation",
                context_id=entry.entry_id,
            )
        )
    if entry.calls:
        output.append("<ul>\n")
        for call in entry.calls:
            call_label = _citation_call_label(call, model, gramps_type_labels)
            output.append(
                f'<li><a href="#{_attr(call.context_id)}">'
                f"{_text(call_label)}</a></li>\n"
            )
        output.append("</ul>\n")
    output.append("</article>\n")
    return "".join(output)


def _citation_call_label(call, model, gramps_type_labels=None) -> str:
    owner = owner_label(model, call.owner_type)
    detail = ""
    if call.owner_type == "event":
        event = model.events.get(call.owner_handle)
        if event is not None:
            parts = [
                gramps_type_label("event", event.type, gramps_type_labels),
                event.date.display if event.date is not None else "",
                event.description,
            ]
            if event.place_handle:
                place = model.places.get(event.place_handle)
                if place is not None:
                    parts.append(place.title or place.name)
            detail = " — ".join(value for value in parts if value)
    elif call.owner_type == "person":
        person = next(
            (
                person
                for person in model.people
                if person.handle == call.owner_handle
            ),
            None,
        )
        if person is not None:
            detail = person.name
    elif call.owner_type == "family":
        family = model.families.get(call.owner_handle)
        if family is not None:
            names = [
                person.name or person.gramps_id
                for person in (family.father, family.mother)
                if person is not None and (person.name or person.gramps_id)
            ]
            detail = f" {label(model, 'and')} ".join(names)
    elif call.owner_type == "place":
        place = model.places.get(call.owner_handle)
        if place is not None:
            detail = place.title or place.name
    elif call.owner_type == "media":
        media = model.media.get(call.owner_handle)
        if media is not None:
            detail = media.description
    return f"{owner} : {detail}" if detail else owner


def _citation_urls(entry, model) -> list[tuple[str, str]]:
    citation = model.citations.get(entry.citation_handle)
    source = model.sources.get(entry.source_handle) if entry.source_handle else None
    url_records = list(getattr(citation, "urls", ()))
    url_records.extend(getattr(source, "urls", ()))
    for reference in entry.repository_refs:
        repository = model.repositories.get(reference.repository_handle)
        url_records.extend(getattr(repository, "urls", ()))

    result = []
    seen = set()
    for url in url_records:
        target = safe_html_url(getattr(url, "path", ""))
        if target is None or target in seen:
            continue
        seen.add(target)
        result.append((target, getattr(url, "description", "")))
    return result


def _render_html_url(target: str, description: str, *, class_name: str) -> str:
    detail = (
        f' <span class="muted">— {_text(description)}</span>'
        if description and description != target
        else ""
    )
    return (
        f'<a class="{_attr(class_name)}" href="{_attr(target)}">'
        f"{_text(target)}</a>{detail}"
    )


def _media_context(model, enabled: bool) -> dict:
    editorial = getattr(model, "editorial_book", None)
    placements = getattr(editorial, "media_placements", ()) if editorial is not None else ()
    return {
        "enabled": enabled,
        "placements": {placement.media_handle: placement for placement in placements},
        "emitted_featured": set(),
        "emitted_shared_assets": set(),
    }


def _render_cover_portraits(model, people, media_context) -> str:
    if not media_context["enabled"]:
        return ""
    editorial = getattr(model, "editorial_book", None)
    if editorial is None:
        return ""
    output = [
        f'<div class="cover-portraits" role="group" aria-label="{_attr(label(model, "couple_portraits"))}">\n'
    ]
    for portrait in editorial.cover_portraits:
        person = people.get(portrait.person_handle)
        output.append(
            _render_media_reference(
                portrait.media_ref,
                portrait.caption,
                model,
                media_context,
                context_type="cover",
                context_id="cover",
                alt=(
                    portrait.caption.strip()
                    or f"{label(model, 'portrait_of')} {_person_name(person, portrait.person_handle)}"
                ),
            )
        )
    output.append("</div>\n")
    rendered = "".join(output)
    return rendered if "<figure" in rendered or "<p class=\"media-reference\"" in rendered else ""


def _portrait_alt(person_handle: str, model) -> str:
    person = next(
        (person for person in getattr(model, "people", ()) if person.handle == person_handle),
        None,
    )
    return f"{label(model, 'portrait_of')} {_person_name(person, person_handle)}"


def _render_media_reference(
    reference,
    caption: str,
    model,
    media_context,
    *,
    context_type: str,
    context_id: str,
    alt: str | None = None,
) -> str:
    if not media_context["enabled"]:
        return ""
    placement = media_context["placements"].get(reference.media_handle)
    media = getattr(model, "media", {}).get(reference.media_handle)
    display_label = (
        caption or (media.description if media is not None else "") or label(model, "document")
    )

    if placement is not None and placement.is_featured and context_type not in {
        "cover",
        "portrait",
    }:
        primary_use = _featured_media_primary_use(placement)
        is_primary = (
            primary_use is not None
            and primary_use.context_type == context_type
            and primary_use.context_id == context_id
            and primary_use.media_ref == reference
        )
        if not is_primary or placement.placement_id in media_context["emitted_featured"]:
            return _media_reference_link(placement.placement_id, display_label, model)
        media_context["emitted_featured"].add(placement.placement_id)
        return _render_media_figure(
            reference,
            display_label,
            model,
            featured=True,
            target_id=placement.placement_id,
            alt=alt,
        )

    artifact = _media_artifact(reference, model)
    asset_href = _html_asset_href(artifact)
    if placement is not None and asset_href is not None:
        same_asset_uses = [
            use
            for use in placement.uses
            if use.media_ref.media_handle == reference.media_handle
            and use.media_ref.rectangle == reference.rectangle
        ]
        if len(same_asset_uses) > 1:
            target_id = f"media-{artifact.cache_key}"
            if asset_href in media_context["emitted_shared_assets"]:
                return _media_reference_link(target_id, display_label, model)
            media_context["emitted_shared_assets"].add(asset_href)
            return _render_media_figure(
                reference,
                display_label,
                model,
                target_id=target_id,
                alt=alt,
            )

    return _render_media_figure(reference, display_label, model, alt=alt)


def _featured_media_primary_use(placement):
    for context_type in ("family_notice", "profile"):
        use = next(
            (candidate for candidate in placement.uses if candidate.context_type == context_type),
            None,
        )
        if use is not None:
            return use
    return placement.uses[0] if placement.uses else None


def _media_reference_link(target_id: str, caption: str, model) -> str:
    return (
        f'<p class="media-reference"><a href="#{_attr(target_id)}">'
        f"{_text(label(model, 'see_reproduction'))} {_text(caption)}</a></p>\n"
    )


def _render_media_figure(
    reference,
    caption: str,
    model,
    *,
    featured: bool = False,
    target_id: str | None = None,
    alt: str | None = None,
) -> str:
    media = getattr(model, "media", {}).get(reference.media_handle)
    artifact = _media_artifact(reference, model)
    asset_href = _html_asset_href(artifact)
    if asset_href is not None:
        image_alt = alt or caption or (media.description if media is not None else "")
        if not image_alt:
            image_alt = label(model, "document_image_no_description")
        dimensions = ""
        width = getattr(artifact, "width", None)
        height = getattr(artifact, "height", None)
        if isinstance(width, int) and not isinstance(width, bool) and width > 0:
            dimensions += f' width="{width}"'
        if isinstance(height, int) and not isinstance(height, bool) and height > 0:
            dimensions += f' height="{height}"'
        target = f' id="{_attr(target_id)}"' if target_id else ""
        class_name = "featured-media" if featured else "media-image"
        output = [
            f'<figure{target} class="media-item {class_name}">\n',
            f'<img src="{_attr(asset_href)}" alt="{_attr(image_alt)}"{dimensions}>\n',
        ]
        if caption:
            output.append(f"<figcaption>{_text(caption)}</figcaption>\n")
        output.append("</figure>\n")
        return "".join(output)

    link_items = _media_external_links(artifact, reference, model)
    fallback = _text(
        caption or (media.description if media is not None else label(model, "document"))
    )
    target = f' id="{_attr(target_id)}"' if target_id else ""
    if link_items:
        links = " · ".join(link_items)
        return (
            f'<p{target} class="media-reference">{fallback} — {links}</p>\n'
        )
    message = label(model, "reproduction_unavailable" if featured else "document_reference")
    return f'<p{target} class="media-reference">{fallback} — {message}.</p>\n'


def _media_artifact(reference, model):
    return next(
        (
            item
            for item in getattr(model, "media_artifacts", ())
            if item.media_handle == reference.media_handle
            and item.rectangle == reference.rectangle
        ),
        None,
    )


def _html_asset_href(artifact) -> str | None:
    if artifact is None or getattr(artifact, "action", None) != "reproduce":
        return None
    cache_key = getattr(artifact, "cache_key", None)
    asset_path = getattr(artifact, "asset_path", None)
    if (
        not isinstance(cache_key, str)
        or len(cache_key) != 64
        or any(char not in "0123456789abcdef" for char in cache_key)
        or not isinstance(asset_path, str)
    ):
        return None
    path = PurePosixPath(asset_path)
    if (
        path.is_absolute()
        or len(path.parts) != 2
        or path.parts[0] in {".", ".."}
        or path.parts[1] != f"{cache_key}.png"
        or any(char in asset_path for char in "\\{}%#\n\r\0")
    ):
        return None
    return f"media/{cache_key}.png"


def _media_external_links(artifact, reference, model) -> list[str]:
    citation_handles = list(getattr(artifact, "citation_handles", ()))
    citation_handles.extend(getattr(reference, "citations", ()))
    media = getattr(model, "media", {}).get(reference.media_handle)
    if media is not None:
        links = getattr(media, "links", None)
        citation_handles.extend(getattr(links, "citations", ()))
    links = []
    for citation_handle in dict.fromkeys(citation_handles):
        citation = getattr(model, "citations", {}).get(citation_handle)
        if citation is None:
            continue
        urls = list(getattr(citation, "urls", ()))
        source_handle = getattr(citation, "source_handle", None)
        source = getattr(model, "sources", {}).get(source_handle) if source_handle else None
        urls.extend(getattr(source, "urls", ()))
        for url in urls:
            target = safe_html_url(url.path)
            if target is None or target in links:
                continue
            links.append(_render_html_url(target, url.description, class_name="media-url"))
    return links


def _book_title(model, editorial) -> str:
    note = _book_note(model, editorial, "BOOK_TITLE")
    fallback = label(model, "book_title_fallback")
    if note is None:
        return fallback
    return render_html_inline_text(note) or fallback


def _render_cover_note(model, editorial, role) -> str:
    note = _book_note(model, editorial, role)
    return render_html_inline_note(note) if note is not None else ""


def _book_note(model, editorial, role):
    if editorial is None:
        return None
    for item in editorial.front_matter_notes:
        if item.role == role:
            return model.notes.get(item.note_handle)
    return None


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


def _text(value) -> str:
    return escape("" if value is None else str(value), quote=False)


def _attr(value) -> str:
    return escape("" if value is None else str(value), quote=True)
