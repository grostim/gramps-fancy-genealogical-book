"""LaTeX renderer for the genealogy book."""

from pathlib import PurePosixPath

from ..book_language import model_book_language
from ..conventions import (
    BOOK_AUTHOR,
    BOOK_DEDICATION,
    BOOK_INTRODUCTION,
    BOOK_PUBLICATION_DATE,
    BOOK_SUBTITLE,
    BOOK_TITLE,
)
from ..domain import (
    BookModel,
    EditorialCitationCall,
    EditorialCitationEntry,
    EditorialFamilyNotice,
    EditorialMediaArtifact,
    EditorialMediaPlacement,
    EditorialMediaUse,
    EditorialPortrait,
    EditorialProfile,
    FamilySection,
    GenealogyPart,
    Media,
    MediaReference,
    Note,
    Person,
    PersonOccurrence,
    RepositoryReference,
    Url,
)
from .citation_numbers import citation_number_map
from .labels import (
    gramps_type_label as _shared_gramps_type_label,
)
from .labels import (
    label as _shared_label,
)
from .labels import (
    label_for_language,
)
from .labels import (
    owner_label as _shared_owner_label,
)
from .latex_notes import render_latex_note
from .latex_text import escape_latex_text, format_latex_url


def label(model: BookModel, key: str) -> str:
    """Use English for legacy direct renderer calls without language metadata."""
    return _shared_label(model, key, default="en")


def owner_label(model: BookModel, owner_type: str) -> str:
    """Use the LaTeX renderer's English fallback for record type labels."""
    return _shared_owner_label(model, owner_type, default="en")


def _front_matter_notes_by_role(model: BookModel) -> dict[str, Note]:
    editorial_book = model.editorial_book
    if editorial_book is None:
        return {}
    return {
        item.role: note
        for item in editorial_book.front_matter_notes
        if (note := model.notes.get(item.note_handle)) is not None
    }


def _render_cover(model: BookModel) -> str:
    """Render the generated cover and any available partner portrait medallions."""
    family = model.reference_family
    partners = [
        person for person in (family.father, family.mother) if person is not None
    ]
    couple_names = label(model, "and").join(
        person.name or person.handle for person in partners
    )
    fallback_subtitle = couple_names or family.gramps_id or family.handle
    safe_handle = "".join(
        character for character in family.handle if character.isalnum() or character in "_-"
    )
    role_notes = _front_matter_notes_by_role(model)
    title_note = role_notes.get(BOOK_TITLE)
    subtitle_note = role_notes.get(BOOK_SUBTITLE)

    output = [
        f"% Gramps family handle: {safe_handle}\n",
        "\\begin{titlepage}\n"
        "\\thispagestyle{empty}\n"
        "\\centering\n"
        "\\vspace*{2.4cm}\n",
    ]
    if title_note is not None:
        output.extend(
            (
                "{\\Large\\bfseries\n",
                render_latex_note(title_note),
                "\\par}\n",
            )
        )
    else:
        output.append(
            "{\\Large\\bfseries "
            + escape_latex_text(label(model, "family_history"))
            + "\\par}\n"
        )

    output.append("\\vspace{0.7cm}\n")
    if subtitle_note is not None:
        output.extend(
            (
                "{\\Huge\\bfseries\n",
                render_latex_note(subtitle_note),
                "\\par}\n",
            )
        )
        if couple_names:
            output.append(
                f"{{\\large {escape_latex_text(couple_names)}\\par}}\n"
            )
    else:
        output.append(
            f"{{\\Huge\\bfseries {escape_latex_text(fallback_subtitle)}\\par}}\n"
        )
    output.append("\\vspace{1.8cm}\n")

    people_by_handle = {person.handle: person for person in model.people}
    portraits = (
        model.editorial_book.cover_portraits
        if model.editorial_book is not None
        else ()
    )
    rendered_portraits = []
    for portrait in portraits[:2]:
        person = people_by_handle.get(portrait.person_handle)
        portrait_label = (person.name if person is not None else "") or portrait.person_handle
        graphic = _render_cover_portrait(
            portrait,
            model.media_artifacts,
            model.media,
            model_book_language(model, default="en"),
            portrait_label,
        )
        if graphic:
            rendered_portraits.append((graphic, portrait_label))

    if rendered_portraits:
        output.append("\\begin{center}\n")
        for index, (graphic, portrait_label) in enumerate(rendered_portraits):
            if index:
                output.append("\\hspace{0.04\\textwidth}\n")
            output.append(
                "\\begin{minipage}[t]{0.4\\textwidth}\n"
                "\\centering\n"
                f"{graphic}\\par\\smallskip\n"
                f"{{\\large {escape_latex_text(portrait_label)}\\par}}\n"
                "\\end{minipage}\n"
            )
        output.append("\\end{center}\n")
    else:
        output.append("\\vspace{1cm}\n")

    for role, style in (
        (BOOK_AUTHOR, "\\large\\itshape " + label(model, "by")),
        (BOOK_PUBLICATION_DATE, "\\large "),
    ):
        note = role_notes.get(role)
        if note is not None:
            output.append("{" + style)
            output.append(render_latex_note(note))
            output.append("\\par}\n")

    output.extend(("\\vfill\n", "\\end{titlepage}\n"))
    return "".join(output)


def _render_front_matter(model: BookModel) -> str:
    role_notes = _front_matter_notes_by_role(model)
    output = []
    for role, heading in (
        (BOOK_DEDICATION, label(model, "dedication")),
        (BOOK_INTRODUCTION, label(model, "introduction")),
    ):
        note = role_notes.get(role)
        if note is None:
            continue
        output.extend(
            (
                "\\clearpage\n",
                f"\\section*{{{heading}}}\n",
                f"\\markboth{{{heading}}}{{}}\n",
                render_latex_note(note),
                "\\clearpage\n",
            )
        )
    return "".join(output)

def _render_cover_portrait(
    portrait: EditorialPortrait,
    artifacts: list[EditorialMediaArtifact],
    media_by_handle: dict[str, Media],
    language: str,
    person_name: str,
) -> str:
    """Return a centered, circularly clipped image for one safe cover artifact."""
    media_ref = portrait.media_ref
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

    width = artifact.width
    height = artifact.height
    dimensions_known = (
        isinstance(width, (int, float))
        and not isinstance(width, bool)
        and isinstance(height, (int, float))
        and not isinstance(height, bool)
        and width > 0
        and height > 0
    )
    fit_dimension = (
        "height=3.2cm"
        if dimensions_known and width > height
        else "width=3.2cm"
    )
    alt = _media_alt_text(
        media_ref,
        portrait.caption,
        media_by_handle,
        language,
        contextual_alt=(
            f"{label_for_language(language, 'portrait_of')} {person_name}"
            if person_name
            else ""
        ),
    )
    graphic = (
        "\\includegraphics["
        + "artifact,"
        + fit_dimension
        + "]{\\detokenize{"
        + path
        + "}}"
    )
    return (
        f"\\begin{{tikzpicture}}[alt={{{alt}}}]\n"
        "\\begin{scope}\n"
        "\\clip (0,0) circle (1.6cm);\n"
        f"\\node[inner sep=0pt] at (0,0) {{{graphic}}};\n"
        "\\end{scope}\n"
        "\\draw[line width=0.6pt] (0,0) circle (1.6cm);\n"
        "\\end{tikzpicture}\n"
    )


def render_latex(
    model: BookModel,
    *,
    gramps_type_labels: dict[tuple[str, str], str] | None = None,
) -> str:
    language = model_book_language(model, default="en")
    babel_language = "french" if language == "fr" else "english"
    pdf_language = "fr-FR" if language == "fr" else "en-US"
    # ulem draws \sout but omits its PDF TextDecorationType layout attribute.
    document = [
        f"\\DocumentMetadata{{lang={pdf_language},tagging=on}}\n"
        "\\documentclass[a4paper]{article}\n"
        f"\\usepackage[{babel_language}]{{babel}}\n"
        "\\usepackage{xurl}\n\\usepackage[hidelinks]{hyperref}\n\\usepackage{graphicx}\n"
        "\\newcommand{\\bookurl}[3]{\\href{#1}{{\\useOriginalUrlSetting\\nolinkurl{#2}}\\nolinkurl{#3}}}\n"
        "\\usepackage[normalem]{ulem}\n\\usepackage{textcomp}\n"
        "\\tagpdfsetup{role/new-attribute={gfb-strikethrough}{/O/Layout/TextDecorationType/LineThrough}}\n"
        "\\NewCommandCopy{\\gfbOriginalSout}{\\sout}\n"
        "\\RenewDocumentCommand{\\sout}{m}{%\n"
        "  \\leavevmode\n"
        "  \\tagmcend\n"
        "  \\tagstructbegin{tag=Span,attribute-class={gfb-strikethrough}}%\n"
        "  \\tagmcbegin{}%\n"
        "  \\gfbOriginalSout{#1}%\n"
        "  \\tagmcend\n"
        "  \\tagstructend\n"
        "  \\tagmcbegin{}%\n"
        "}\n"
        "\\usepackage{tikz}\n\\usepackage{fancyhdr}\n"
        "\\renewcommand{\\familydefault}{\\sfdefault}\n"
        "\\pagestyle{fancy}\n"
        "\\fancyhf{}\n"
        "\\fancyhead[L]{\\parbox[t]{\\headwidth}{\\footnotesize"
        "\\nouppercase{\\leftmark}\\hfill\\thepage\\\\[4pt]"
        "\\nouppercase{\\rightmark}}}\n"
        "\\fancyhead[R]{}\n"
        "\\renewcommand{\\headrulewidth}{0.2pt}\n"
        "\\setlength{\\headheight}{30pt}\n"
        "\\setlength{\\headsep}{18pt}\n"
        "\\setlength{\\emergencystretch}{2em}\n"
        "\\begin{document}\n",
        _render_cover(model),
    ]
    document.append(_render_front_matter(model))
    document.append(
        "\\markboth{"
        + escape_latex_text(label(model, "contents"))
        + "}{}\n\\tableofcontents\n\\clearpage\n"
    )

    emitted_targets: set[str] = set()
    people_by_handle = {person.handle: person for person in model.people}
    citation_by_call = {
        call.call_id: entry
        for entry in (
            model.editorial_book.citation_entries if model.editorial_book else ()
        )
        for call in entry.calls
    }
    citation_numbers = citation_number_map(model.editorial_book)
    if model.genealogy is not None:
        for part in (model.genealogy.ancestry, model.genealogy.descent):
            document.append(
                _render_genealogy_part(
                    part,
                    people_by_handle,
                    emitted_targets,
                    model,
                )
            )
        if model.genealogy.family_sections:
            occurrences_by_id = {
                occurrence.occurrence_id: occurrence
                for part in (model.genealogy.ancestry, model.genealogy.descent)
                for generation in part.generations
                for occurrence in generation.occurrences
            }
            document.append(
                _render_family_sections(
                    model.genealogy.family_sections,
                    model,
                    occurrences_by_id,
                    emitted_targets,
                    gramps_type_labels,
                )
            )

    if model.editorial_book is not None and model.editorial_book.family_notices:
        document.append(_section_heading(label(model, "family_notices")))
        for notice in model.editorial_book.family_notices:
            document.append(
                _render_family_notice(
                    notice,
                    model,
                    emitted_targets,
                    citation_by_call,
                    citation_numbers,
                    gramps_type_labels,
                )
            )

    if model.editorial_book is not None and model.editorial_book.profiles:
        document.append(_section_heading(label(model, "person_profiles")))
        for profile in model.editorial_book.profiles:
            document.append(
                _render_profile(
                    profile,
                    model,
                    people_by_handle,
                    emitted_targets,
                    citation_by_call,
                    citation_numbers,
                    gramps_type_labels,
                )
            )

    if model.editorial_book is not None and model.editorial_book.citation_entries:
        document.append(
            _render_citation_appendix(
                model.editorial_book.citation_entries,
                model,
                emitted_targets,
                citation_numbers,
                gramps_type_labels,
            )
        )

    if model.editorial_book is not None and model.editorial_book.person_index:
        targets = {
            target.target_id: target
            for target in model.editorial_book.navigation_targets
        }
        document.append(_section_heading(label(model, "person_index")))
        document.append("\\begin{itemize}\n")
        for entry in model.editorial_book.person_index:
            display_name = entry.display_name or entry.person_handle
            display_label = escape_latex_text(display_name)
            document.append(
                f"\\item {_latex_anchor(entry.entry_id, emitted_targets)}"
            )
            target = targets.get(entry.target_id)
            if (
                target is not None
                and target.availability == "available"
                and entry.target_id in emitted_targets
            ):
                display_label = _latex_page_link(entry.target_id, display_name)
            document.append(f"{display_label}\n")
        document.append("\\end{itemize}\n")

    document.append("\\end{document}\n")
    return "".join(document)


def _render_genealogy_part(
    part: GenealogyPart,
    people_by_handle: dict[str, Person],
    emitted_targets: set[str],
    model: BookModel,
) -> str:
    if not part.generations:
        return ""

    first_generation = part.generations[0]
    first_occurrence = (
        first_generation.occurrences[0]
        if first_generation.occurrences
        else None
    )
    first_context = _running_context_label(
        first_generation.number,
        first_occurrence.branch_handles if first_occurrence is not None else (),
        people_by_handle,
        model,
    )
    part_name = label(model, part.name.casefold())
    if part_name == part.name.casefold():
        part_name = part.name.title()
    output = [_section_heading(part_name, first_context)]
    for generation in part.generations:
        previous_branches = None
        if generation.occurrences:
            first_branches = generation.occurrences[0].branch_handles
            output.append(
                "\\markright{"
                + escape_latex_text(
                    _running_context_label(
                        generation.number,
                        first_branches,
                        people_by_handle,
                        model,
                    )
                )
                + "}\n"
            )
            previous_branches = first_branches
        else:
            output.append(
                "\\markright{"
                + escape_latex_text(
                    _running_context_label(
                        generation.number, (), people_by_handle, model
                    )
                )
                + "}\n"
            )
        output.append(
            f"\\subsection*{{{escape_latex_text(label(model, 'generation'))} {generation.number}}}\n"
            "\\begin{itemize}\n"
        )
        for occurrence in generation.occurrences:
            if occurrence.branch_handles != previous_branches:
                output.append(
                    "\\markright{"
                    + escape_latex_text(
                        _running_context_label(
                            generation.number,
                            occurrence.branch_handles,
                            people_by_handle,
                            model,
                        )
                    )
                    + "}\n"
                )
                previous_branches = occurrence.branch_handles
            person = people_by_handle.get(occurrence.person_handle)
            name = person.name if person is not None else ""
            name = name or occurrence.person_handle
            output.append("\\item ")
            target_id = occurrence.occurrence_id
            if target_id and target_id not in emitted_targets:
                output.append(_latex_anchor(target_id, emitted_targets))
            output.append(f"{escape_latex_text(name)}\n")
        output.append("\\end{itemize}\n")
    return "".join(output)


def _render_family_sections(
    sections: tuple[FamilySection, ...],
    model: BookModel,
    occurrences_by_id: dict[str, PersonOccurrence],
    emitted_targets: set[str],
    gramps_type_labels: dict[tuple[str, str], str] | None = None,
) -> str:
    people_by_handle = {person.handle: person for person in model.people}
    notices_by_family = {
        notice.family_handle: notice
        for notice in (model.editorial_book.family_notices if model.editorial_book else ())
    }
    first_section = sections[0]
    output = [
        _section_heading(
            label(model, "family_connections"),
            _running_context_label(
                first_section.generation,
                first_section.branch_handles,
                people_by_handle,
                model,
            ),
        ),
        "\\begin{itemize}\n",
    ]
    for section in sections:
        output.append(
            "\\markright{"
            + escape_latex_text(
                _running_context_label(
                    section.generation,
                    section.branch_handles,
                    people_by_handle,
                    model,
                )
            )
            + "}\n"
        )
        family = model.families.get(section.family_handle)
        partners = [
            _occurrence_link(target_id, occurrences_by_id, people_by_handle, emitted_targets)
            for target_id in section.partner_occurrence_ids
        ]
        children = [
            _occurrence_link(target_id, occurrences_by_id, people_by_handle, emitted_targets)
            for target_id in section.child_occurrence_ids
        ]
        partner_label = label(model, "and").join(item for item in partners if item)
        section_part = label(model, section.part).lower()
        if section_part == section.part:
            section_part = section.part
        title = (
            partner_label
            or escape_latex_text(
                (family.gramps_id if family is not None else "")
                or section.family_handle
            )
        )
        output.append(
            f"\\item {_latex_anchor(section.section_id, emitted_targets)}"
            f"\\textbf{{{title}}}"
            f" ({escape_latex_text(section_part)}, "
            f"{escape_latex_text(label(model, 'generation').lower())} {section.generation})\n"
        )
        notice = notices_by_family.get(section.family_handle)
        if notice is not None:
            output.append(
                "\\par "
                + _latex_page_link(notice.notice_id, label(model, "family_details"))
                + "\n"
            )
        if children:
            output.append(
                "\\par "
                + escape_latex_text(label(model, "children"))
                + ": "
                + ", ".join(item for item in children if item)
                + "\n"
            )
        if section.parent_child_links:
            output.append("\\begin{itemize}\n")
            for link in section.parent_child_links:
                parent = _occurrence_link(
                    link.parent_occurrence_id,
                    occurrences_by_id,
                    people_by_handle,
                    emitted_targets,
                )
                child = _occurrence_link(
                    link.child_occurrence_id,
                    occurrences_by_id,
                    people_by_handle,
                    emitted_targets,
                )
                relationship = _shared_gramps_type_label(
                    "child_relationship",
                    _relationship_label(link.relationship_type),
                    gramps_type_labels,
                )
                suffix = f" ({escape_latex_text(relationship)})" if relationship else ""
                output.append(f"\\item {parent} $\\to$ {child}{suffix}\n")
            output.append("\\end{itemize}\n")
    output.append("\\end{itemize}\n")
    return "".join(output)


def _occurrence_link(
    target_id: str,
    occurrences_by_id: dict[str, PersonOccurrence],
    people_by_handle: dict[str, Person],
    emitted_targets: set[str],
) -> str:
    occurrence = occurrences_by_id.get(target_id)
    person = people_by_handle.get(occurrence.person_handle) if occurrence else None
    label = (person.name if person is not None else "") or (
        occurrence.person_handle if occurrence is not None else target_id
    )
    if target_id in emitted_targets:
        return _latex_page_link(target_id, label)
    return escape_latex_text(label)


def _relationship_label(value: object) -> str:
    if value is None or value is False:
        return ""
    if isinstance(value, dict):
        value = value.get("string", value.get("value", value))
    if isinstance(value, (tuple, list)):
        return ", ".join(str(item) for item in value)
    return str(value)


def _render_profile(
    profile: EditorialProfile,
    model: BookModel,
    people_by_handle: dict[str, Person],
    emitted_targets: set[str],
    citation_by_call: dict[str, EditorialCitationEntry],
    citation_numbers: dict[str, int],
    gramps_type_labels: dict[tuple[str, str], str] | None = None,
) -> str:
    person = people_by_handle.get(profile.person_handle)
    name = person.name if person is not None else ""
    name = name or profile.person_handle
    language = model_book_language(model, default="en")
    output = []
    output.append(_latex_anchor(profile.profile_id, emitted_targets))
    output.append(f"\\subsection*{{{escape_latex_text(name)}}}\n")
    if profile.portrait is not None:
        output.append(
            _render_media_image(
                profile.portrait,
                profile.portrait.caption,
                model.media_artifacts,
                media_by_handle=model.media,
                language=language,
                contextual_alt=f"{label_for_language(language, 'portrait_of')} {name}",
                width="0.75\\linewidth",
            )
        )
    for reference in profile.media_refs:
        placement = _media_placement_for_reference(model, reference)
        if placement is None or not placement.is_featured:
            continue
        primary_use = _featured_media_primary_use(placement)
        if (
            primary_use is not None
            and primary_use.context_type == "profile"
            and primary_use.context_id == profile.profile_id
        ):
            output.append(
                _render_featured_media(
                    placement,
                    primary_use.media_ref,
                    placement.caption,
                    model.media_artifacts,
                    emitted_targets,
                    language,
                    model.media,
                )
            )
        else:
            output.append(
                _render_featured_media_link(
                    placement,
                    placement.caption,
                    emitted_targets,
                    model_book_language(model, default="en"),
                )
            )

    if profile.primary_occurrence_id in emitted_targets:
        output.append(
            "\\noindent "
            + escape_latex_text(label(model, "see"))
            + " "
            + _latex_page_link(
                profile.primary_occurrence_id or "",
                label(model, "first_appearance"),
            )
            + ".\\par\n"
        )

    if profile.event_refs:
        output.append(
            "\\paragraph{" + escape_latex_text(label(model, "events"))
            + "}\n\\begin{itemize}\n"
        )
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
            ) or (
                _shared_gramps_type_label("event", event.type, gramps_type_labels)
                if event is not None
                else ""
            ) or reference.event_handle
            details = []
            if (
                event is not None
                and event.type
                and event.description
                and event.type.casefold() != event.description.casefold()
            ):
                details.append(
                    escape_latex_text(
                        _shared_gramps_type_label(
                            "event", event.type, gramps_type_labels
                        )
                    )
                )
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
                details.append(
                    escape_latex_text(
                        _shared_gramps_type_label(
                            "event_role", reference.role, gramps_type_labels
                        )
                    )
                )
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
        output.append("\\paragraph{" + escape_latex_text(label(model, "notes")) + "}\n")
        for index, note in notes:
            target_id = (
                profile.note_target_ids[index]
                if index < len(profile.note_target_ids)
                else ""
            )
            note_text = render_latex_note(note)
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
        output.append(
            "\\paragraph{" + escape_latex_text(label(model, "sources"))
            + "}\n\\begin{itemize}\n"
        )
        for entry in citation_entries.values():
            output.append(f"\\item {_citation_reference(entry, citation_numbers)}\n")
        output.append("\\end{itemize}\n")
    return "".join(output)


def _render_family_notice(
    notice: EditorialFamilyNotice,
    model: BookModel,
    emitted_targets: set[str],
    citation_by_call: dict[str, EditorialCitationEntry],
    citation_numbers: dict[str, int],
    gramps_type_labels: dict[tuple[str, str], str] | None = None,
) -> str:
    language = model_book_language(model, default="en")
    family = model.families.get(notice.family_handle)
    title = _family_title(family, notice.family_handle, model)
    output = [
        _latex_anchor(notice.notice_id, emitted_targets),
        f"\\subsection*{{{escape_latex_text(title)}}}\n",
    ]
    if notice.primary_section_id in emitted_targets:
        output.append(
            "\\noindent "
            + escape_latex_text(label(model, "see"))
            + " "
            + _latex_page_link(notice.primary_section_id, label(model, "family_section"))
            + ".\\par\n"
        )

    if notice.event_refs:
        output.append(
            "\\paragraph{" + escape_latex_text(label(model, "events"))
            + "}\n\\begin{itemize}\n"
        )
        for index, reference in enumerate(notice.event_refs):
            target_id = (
                notice.event_target_ids[index]
                if index < len(notice.event_target_ids)
                else ""
            )
            anchor = _latex_anchor(target_id, emitted_targets)
            event = model.events.get(reference.event_handle)
            event_name = (
                event.description if event is not None else ""
            ) or (
                _shared_gramps_type_label("event", event.type, gramps_type_labels)
                if event is not None
                else ""
            ) or reference.event_handle
            details = []
            if (
                event is not None
                and event.type
                and event.description
                and event.type.casefold() != event.description.casefold()
            ):
                details.append(
                    escape_latex_text(
                        _shared_gramps_type_label(
                            "event", event.type, gramps_type_labels
                        )
                    )
                )
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
                details.append(
                    escape_latex_text(
                        _shared_gramps_type_label(
                            "event_role", reference.role, gramps_type_labels
                        )
                    )
                )
            suffix = f" ({'; '.join(details)})" if details else ""
            output.append(
                f"\\item {anchor}{escape_latex_text(event_name)}{suffix}\n"
            )
        output.append("\\end{itemize}\n")

    for reference in notice.media_refs:
        media = model.media.get(reference.media_handle)
        placement = _media_placement_for_reference(model, reference)
        caption = (
            placement.caption
            if placement is not None and placement.caption
            else media.description if media is not None else ""
        )
        if placement is not None and placement.is_featured:
            primary_use = _featured_media_primary_use(placement)
            if (
                primary_use is not None
                and primary_use.context_type == "family_notice"
                and primary_use.context_id == notice.notice_id
            ):
                output.append(
                    _render_featured_media(
                        placement,
                        primary_use.media_ref,
                        caption,
                        model.media_artifacts,
                        emitted_targets,
                        language,
                        model.media,
                    )
                )
            else:
                output.append(
                    _render_featured_media_link(
                        placement,
                        caption,
                        emitted_targets,
                        model_book_language(model, default="en"),
                    )
                )
        else:
            output.append(
                _render_media_image(
                    reference,
                    caption,
                    model.media_artifacts,
                    media_by_handle=model.media,
                    language=language,
                    width="0.7\\linewidth",
                )
            )

    notes = []
    for index, handle in enumerate(notice.note_handles):
        note = model.notes.get(handle)
        if note is not None and note.is_publishable:
            notes.append((index, note))
    if notes:
        output.append("\\paragraph{" + escape_latex_text(label(model, "notes")) + "}\n")
        for index, note in notes:
            target_id = (
                notice.note_target_ids[index]
                if index < len(notice.note_target_ids)
                else ""
            )
            note_text = render_latex_note(note)
            output.append(
                f"{_latex_anchor(target_id, emitted_targets)}\\begin{{quote}}\n"
                f"{note_text}\n"
                "\\end{quote}\n"
            )

    citations = {
        citation_by_call[call_id].entry_id: citation_by_call[call_id]
        for call_id in notice.citation_call_ids
        if call_id in citation_by_call
    }
    if citations:
        output.append(
            "\\paragraph{" + escape_latex_text(label(model, "sources"))
            + "}\n\\begin{itemize}\n"
        )
        for entry in citations.values():
            output.append(f"\\item {_citation_reference(entry, citation_numbers)}\n")
        output.append("\\end{itemize}\n")
    return "".join(output)


def _family_title(family, fallback: str, model: BookModel) -> str:
    if family is None:
        return fallback
    partners = [
        person.name or person.handle
        for person in (family.father, family.mother)
        if person is not None
    ]
    return label(model, "and").join(partners) or family.gramps_id or family.handle or fallback


def _render_citation_appendix(
    entries: tuple[EditorialCitationEntry, ...],
    model: BookModel,
    emitted_targets: set[str],
    citation_numbers: dict[str, int],
    gramps_type_labels: dict[tuple[str, str], str] | None = None,
) -> str:
    output = [
        _section_heading(label(model, "documentary_appendix")),
        "\\begin{itemize}\n",
    ]
    profiles = {
        profile.profile_id: profile
        for profile in (model.editorial_book.profiles if model.editorial_book else ())
    }
    notices = {
        notice.notice_id: notice
        for notice in (
            model.editorial_book.family_notices if model.editorial_book else ()
        )
    }
    people_by_handle = {person.handle: person for person in model.people}
    ordered_entries = sorted(entries, key=lambda entry: citation_numbers.get(entry.entry_id, 0))
    for entry in ordered_entries:
        citation = model.citations.get(entry.citation_handle)
        source_handle = entry.source_handle or (
            citation.source_handle if citation is not None else None
        )
        source = model.sources.get(source_handle) if source_handle else None
        citation_number = citation_numbers.get(entry.entry_id)
        number_label = f"[{citation_number}] " if citation_number is not None else ""
        output.append(
            f"\\item {_latex_anchor(entry.entry_id, emitted_targets)}"
            f"\\textbf{{{number_label}{escape_latex_text(_citation_title(entry, model))}}}\n"
        )
        details = []
        if source is not None and source.author:
            details.append(escape_latex_text(source.author))
        if source is not None and source.publication_info:
            details.append(escape_latex_text(source.publication_info))
        if citation is not None and citation.page:
            details.append(
                f"{escape_latex_text(label(model, 'page_abbreviation'))} "
                f"{escape_latex_text(citation.page)}"
            )
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
            output.append("\\par " + escape_latex_text(label(model, "repositories")) + ": ")
            output.append(
                "; ".join(
                    _format_repository(repository_name, reference)
                    for repository_name, reference in repositories
                )
            )
            output.append("\n")

        if urls:
            output.append("\\par " + escape_latex_text(label(model, "urls")) + ": ")
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
                "\\par " + escape_latex_text(label(model, "media")) + ": "
                + "; ".join(
                    escape_latex_text(media_label) for media_label in media_labels
                )
                + "\n"
            )
        for reference in entry.media_refs:
            media = model.media.get(reference.media_handle)
            placement = _media_placement_for_reference(model, reference)
            caption = (
                placement.caption
                if placement is not None and placement.caption
                else media.description if media is not None else ""
            )
            if placement is not None and placement.is_featured:
                primary_use = _featured_media_primary_use(placement)
                if (
                    primary_use is not None
                    and primary_use.context_type == "citation"
                    and primary_use.context_id == entry.entry_id
                ):
                    output.append(
                        _render_featured_media(
                            placement,
                            primary_use.media_ref,
                            caption,
                            model.media_artifacts,
                            emitted_targets,
                            model_book_language(model, default="en"),
                            model.media,
                        )
                    )
                else:
                    output.append(
                        _render_featured_media_link(
                            placement,
                            caption,
                            emitted_targets,
                            model_book_language(model, default="en"),
                        )
                    )
            else:
                output.append(
                    _render_shared_media_reference(
                        reference,
                        caption,
                        placement,
                        model.media_artifacts,
                        emitted_targets,
                        model_book_language(model, default="en"),
                        media_by_handle=model.media,
                        width="0.6\\linewidth",
                    )
                )

        call_labels = [
            (
                call,
                _citation_call_label(
                    call,
                    profiles,
                    notices,
                    people_by_handle,
                    model,
                    gramps_type_labels,
                ),
            )
            for call in entry.calls
        ]
        if call_labels:
            output.append("\\begin{itemize}\n")
            for call, call_label in call_labels:
                context_profile = profiles.get(call.context_id)
                context_notice = notices.get(call.context_id)
                context_target = (
                    context_profile.profile_id
                    if context_profile is not None
                    else context_notice.notice_id if context_notice is not None else ""
                )
                linked_label = (
                    _latex_page_link(context_target, call_label)
                    if context_target and context_target in emitted_targets
                    else escape_latex_text(call_label)
                )
                output.append(
                    f"\\item {_latex_anchor(call.call_id, emitted_targets)}"
                    f"{linked_label}\n"
                )
            output.append("\\end{itemize}\n")
    output.append("\\end{itemize}\n")
    return "".join(output)


def _citation_reference(
    entry: EditorialCitationEntry, citation_numbers: dict[str, int]
) -> str:
    number = citation_numbers.get(entry.entry_id)
    label = f"[{number}]" if number is not None else entry.entry_id
    return _latex_page_link(entry.entry_id, label)


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
    notices: dict[str, EditorialFamilyNotice],
    people_by_handle: dict[str, Person],
    model: BookModel,
    gramps_type_labels: dict[tuple[str, str], str] | None = None,
) -> str:
    profile = profiles.get(call.context_id)
    person = people_by_handle.get(profile.person_handle) if profile is not None else None
    notice = notices.get(call.context_id)
    family = model.families.get(notice.family_handle) if notice is not None else None
    context_name = (
        person.name
        if person is not None
        else _family_title(family, notice.family_handle, model) if notice is not None else ""
    )
    if call.owner_type == "event":
        event = model.events.get(call.owner_handle)
        owner_name = (
            (
                event.description
                or _shared_gramps_type_label(
                    "event", event.type, gramps_type_labels
                )
                or event.gramps_id
            )
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
        owner_name = (note.gramps_id or label(model, "owner_note")) if note is not None else ""
    elif call.owner_type == "family":
        owner_name = _family_title(
            model.families.get(call.owner_handle), call.owner_handle, model
        )
    else:
        owner_name = person.name if call.owner_type == "person" and person else ""
    owner_name = owner_name or call.owner_handle
    owner_type = owner_label(model, call.owner_type)
    if context_name:
        return f"{context_name} — {owner_type}: {owner_name}"
    return f"{owner_type}: {owner_name}"


def _unique_urls(urls: list[Url]) -> tuple[Url, ...]:
    seen = set()
    unique = []
    for url in urls:
        if url.path not in seen:
            unique.append(url)
            seen.add(url.path)
    return tuple(unique)


def _media_placement_for_reference(
    model: BookModel, reference: MediaReference
) -> EditorialMediaPlacement | None:
    editorial_book = model.editorial_book
    if editorial_book is None:
        return None
    return next(
        (
            placement
            for placement in editorial_book.media_placements
            if placement.media_handle == reference.media_handle
        ),
        None,
    )


def _featured_media_primary_use(
    placement: EditorialMediaPlacement,
) -> EditorialMediaUse | None:
    for context_type in ("family_notice", "profile"):
        use = next(
            (
                candidate
                for candidate in placement.uses
                if candidate.context_type == context_type
            ),
            None,
        )
        if use is not None:
            return use
    return placement.uses[0] if placement.uses else None


def _render_featured_media_link(
    placement: EditorialMediaPlacement,
    caption: str,
    emitted_targets: set[str],
    language: str,
) -> str:
    if placement.placement_id not in emitted_targets:
        display_label = escape_latex_text(
            caption or label_for_language(language, "featured_image")
        )
        unavailable = label_for_language(language, "reproduction_unavailable")
        return f"\\par {display_label} ({unavailable}).\\par\n"
    display_label = caption or label_for_language(language, "featured_image")
    return (
        "\\par "
        + escape_latex_text(label_for_language(language, "full_page_reproduction"))
        + " "
        + _latex_page_link(placement.placement_id, display_label)
        + ".\\par\n"
    )


def _render_featured_media(
    placement: EditorialMediaPlacement,
    reference: MediaReference,
    caption: str,
    artifacts: list[EditorialMediaArtifact],
    emitted_targets: set[str],
    language: str,
    media_by_handle: dict[str, Media],
) -> str:
    if placement.placement_id in emitted_targets:
        return _render_featured_media_link(placement, caption, emitted_targets, language)

    artifact = next(
        (
            item
            for item in artifacts
            if item.media_handle == reference.media_handle
            and item.rectangle == reference.rectangle
            and item.action == "reproduce"
        ),
        None,
    )
    path = (
        _safe_latex_media_path(artifact.asset_path, artifact.cache_key)
        if artifact is not None and artifact.asset_path is not None
        else None
    )
    if path is None:
        display_label = escape_latex_text(
            caption or label_for_language(language, "featured_image")
        )
        unavailable = label_for_language(language, "reproduction_unavailable")
        return f"\\par {display_label} ({unavailable}).\\par\n"

    anchor = _latex_anchor(placement.placement_id, emitted_targets)
    output = [
        "\\clearpage\n"
        "\\thispagestyle{fancy}\n"
        f"{anchor}\n"
        "\\begin{center}\n"
        f"\\includegraphics[width=0.92\\textwidth,height=0.80\\textheight,"
        f"alt={{{_media_alt_text(reference, caption, media_by_handle, language)}}},"
        f"keepaspectratio]{{\\detokenize{{{path}}}}}\\par\n"
    ]
    if caption:
        output.append(f"{{\\small {escape_latex_text(caption)}}}\\par\n")
    output.extend(("\\end{center}\n", "\\clearpage\n"))
    return "".join(output)


def _render_media_image(
    reference: EditorialPortrait | MediaReference,
    caption: str,
    artifacts: list[EditorialMediaArtifact],
    *,
    width: str,
    media_by_handle: dict[str, Media],
    language: str,
    contextual_alt: str = "",
) -> str:
    media_ref = reference.media_ref if isinstance(reference, EditorialPortrait) else reference
    artifact = _reproduced_media_artifact(media_ref, artifacts)
    if artifact is None or artifact.asset_path is None:
        return ""
    path = _safe_latex_media_path(artifact.asset_path, artifact.cache_key)
    if path is None:
        return ""
    alt = _media_alt_text(
        media_ref,
        caption,
        media_by_handle,
        language,
        contextual_alt=contextual_alt,
    )
    output = [
        "\\begin{center}\n"
        f"\\includegraphics[width={width},alt={{{alt}}}]"
        f"{{\\detokenize{{{path}}}}}\n"
        "\\par\n"
    ]
    if caption:
        output.append(f"{{\\small {escape_latex_text(caption)}}}\\par\n")
    output.append("\\end{center}\n")
    return "".join(output)


def _render_shared_media_reference(
    reference: MediaReference,
    caption: str,
    placement: EditorialMediaPlacement | None,
    artifacts: list[EditorialMediaArtifact],
    emitted_targets: set[str],
    language: str,
    media_by_handle: dict[str, Media],
    *,
    width: str,
) -> str:
    same_asset_uses = (
        [
            use
            for use in placement.uses
            if use.media_ref.media_handle == reference.media_handle
            and use.media_ref.rectangle == reference.rectangle
        ]
        if placement is not None
        else []
    )
    artifact = _reproduced_media_artifact(reference, artifacts)
    if len(same_asset_uses) < 2 or artifact is None or artifact.asset_path is None:
        return _render_media_image(
            reference,
            caption,
            artifacts,
            width=width,
            media_by_handle=media_by_handle,
            language=language,
        )

    path = _safe_latex_media_path(artifact.asset_path, artifact.cache_key)
    if path is None or artifact.cache_key is None:
        return _render_media_image(
            reference,
            caption,
            artifacts,
            width=width,
            media_by_handle=media_by_handle,
            language=language,
        )

    target_id = f"media-{artifact.cache_key}"
    if target_id in emitted_targets:
        display_label = caption or label_for_language(
            language, "document_image_no_description"
        )
        return (
            "\\par "
            + escape_latex_text(label_for_language(language, "see_reproduction"))
            + " "
            + _latex_page_link(target_id, display_label)
            + ".\\par\n"
        )

    anchor = _latex_anchor(target_id, emitted_targets)
    return anchor + _render_media_image(
        reference,
        caption,
        artifacts,
        width=width,
        media_by_handle=media_by_handle,
        language=language,
    )


def _media_alt_text(
    reference: EditorialPortrait | MediaReference,
    caption: str,
    media_by_handle: dict[str, Media],
    language: str,
    *,
    contextual_alt: str = "",
) -> str:
    media_ref = reference.media_ref if isinstance(reference, EditorialPortrait) else reference
    media = media_by_handle.get(media_ref.media_handle)
    text = (
        caption.strip()
        or contextual_alt.strip()
        or (media.description.strip() if media is not None else "")
        or label_for_language(language, "document_image_no_description")
    )
    return escape_latex_text(text)


def _reproduced_media_artifact(
    reference: EditorialPortrait | MediaReference,
    artifacts: list[EditorialMediaArtifact],
) -> EditorialMediaArtifact | None:
    media_ref = reference.media_ref if isinstance(reference, EditorialPortrait) else reference
    return next(
        (
            item
            for item in artifacts
            if item.media_handle == media_ref.media_handle
            and item.rectangle == media_ref.rectangle
            and item.action == "reproduce"
        ),
        None,
    )


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


def _latex_page_link(target_id: str, label: str) -> str:
    target = _latex_target(target_id)
    escaped_label = escape_latex_text(label)
    return (
        f"\\hyperlink{{{target}}}{{{escaped_label}}}"
        f" (\\hyperlink{{{target}}}{{p.~\\pageref*{{{target}}}}})"
    )


def _latex_anchor(target_id: str, emitted_targets: set[str]) -> str:
    if not target_id or target_id in emitted_targets:
        return ""
    emitted_targets.add(target_id)
    target = _latex_target(target_id)
    return f"\\hypertarget{{{target}}}{{}}\\label{{{target}}}"


def _running_context_label(
    generation: int,
    branch_handles: tuple[str, ...],
    people_by_handle: dict[str, Person],
    model: BookModel,
) -> str:
    language = model_book_language(model, default="en")
    label = f"{label_for_language(language, 'generation')} {generation}"
    branches = []
    for handle in branch_handles:
        person = people_by_handle.get(handle)
        name = (person.name if person is not None else "") or handle
        if name not in branches:
            branches.append(name)
    if branches:
        label += " / " + label_for_language(language, "branch") + ": " + " + ".join(branches)
    return label


def _section_heading(title: str, context: str = "") -> str:
    escaped = escape_latex_text(title)
    escaped_context = escape_latex_text(context)
    return (
        "\\clearpage\n"
        f"\\section*{{{escaped}}}\n"
        f"\\markboth{{{escaped}}}{{{escaped_context}}}\n"
        f"\\addcontentsline{{toc}}{{section}}{{{escaped}}}\n"
    )


def _latex_target(target_id: str) -> str:
    """Map arbitrary stable model IDs to safe, deterministic hyperref labels."""
    return f"target-{target_id.encode('utf-8').hex()}"
