#!/usr/bin/env python3
"""Check language and structure contracts in renderer-produced tagged PDFs."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader


def _resolved_role(tag: object, role_map: dict[str, str]) -> str:
    role = str(tag)
    visited: set[str] = set()
    while role in role_map and role not in visited:
        visited.add(role)
        role = role_map[role]
    return role


def _count_roles(
    node: object,
    role_map: dict[str, str],
    counts: dict[str, int],
    figures_without_alt: list[str],
) -> None:
    if hasattr(node, "get_object"):
        node = node.get_object()

    if isinstance(node, (list, tuple)):
        for child in node:
            _count_roles(child, role_map, counts, figures_without_alt)
        return

    if not isinstance(node, dict):
        return

    tag = node.get("/S")
    if tag is not None:
        role = _resolved_role(tag, role_map)
        counts[role] = counts.get(role, 0) + 1
        if role == "/Figure":
            alt = node.get("/Alt")
            if alt is None or not str(alt).strip():
                figures_without_alt.append(str(node))

    children = node.get("/K")
    if children is not None:
        _count_roles(children, role_map, counts, figures_without_alt)


def verify(pdf_path: Path, language: str = "fr") -> None:
    pdf_language = {"fr": "fr-FR", "en": "en-US"}[language]
    reader = PdfReader(pdf_path)
    catalog = reader.root_object
    if reader.pdf_header != "%PDF-2.0":
        raise ValueError(f"Expected a PDF 2.0 header; got {reader.pdf_header}.")
    if str(catalog.get("/Lang")) != pdf_language:
        raise ValueError(
            f"Expected PDF language {pdf_language}; got {catalog.get('/Lang')}."
        )

    if reader.metadata is None or not reader.metadata.title:
        raise ValueError("The PDF document title is missing from its metadata.")
    xmp_metadata = reader.xmp_metadata
    if xmp_metadata is None or not xmp_metadata.dc_title:
        raise ValueError("The PDF XMP metadata does not contain dc:title.")

    viewer_preferences = catalog.get("/ViewerPreferences") or {}
    if viewer_preferences.get("/DisplayDocTitle") != True:  # noqa: E712
        raise ValueError("The PDF viewer preferences do not enable DisplayDocTitle.")

    mark_info = catalog.get("/MarkInfo")
    if mark_info is None or mark_info.get("/Marked") != True:  # noqa: E712
        raise ValueError("The PDF catalog does not declare marked content.")

    structure = catalog.get("/StructTreeRoot")
    if structure is None:
        raise ValueError("The PDF has no structure tree.")

    class_map = structure.get("/ClassMap") or {}
    itemize_attributes = class_map.get("/itemize")
    if itemize_attributes is None:
        raise ValueError("The PDF has no itemize list attribute class.")
    if str(itemize_attributes.get("/O")) != "/List":
        raise ValueError("The itemize attribute class is not owned by List.")
    if str(itemize_attributes.get("/ListNumbering")) != "/Unordered":
        raise ValueError("The itemize class is not marked Unordered.")

    role_map = {
        str(source): str(target)
        for source, target in (structure.get("/RoleMap") or {}).items()
    }
    role_counts: dict[str, int] = {}
    figures_without_alt: list[str] = []
    _count_roles(structure.get("/K"), role_map, role_counts, figures_without_alt)
    if role_counts.get("/L", 0) < 1 or role_counts.get("/LI", 0) < 2:
        raise ValueError(
            "The structure tree must contain an L list with at least two LI items; "
            f"found {role_counts}."
        )
    if role_counts.get("/H3", 0) < 1 or role_counts.get("/H4", 0) > 0:
        raise ValueError(
            "Paragraph subheadings must map to H3 without skipping to H4; "
            f"found {role_counts.get('/H3', 0)} H3 and {role_counts.get('/H4', 0)} H4."
        )
    if role_counts.get("/Figure", 0) < 1 or figures_without_alt:
        raise ValueError(
            "Every tagged figure must have non-empty alternative text; "
            f"found {role_counts.get('/Figure', 0)} figure(s), "
            f"{len(figures_without_alt)} without alternative text."
        )

    extraction = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout
    index_label = "Index des personnes" if language == "fr" else "Person index"
    index_start = extraction.rfind(index_label)
    if index_start < 0:
        raise ValueError(f"The {language} person index is missing from extracted text.")
    person_index = extraction[index_start:]
    for name in ("Émile Exemple", "Jeanne Fictive"):
        marker_pattern = (
            rf"—\s+{re.escape(name)}" if language == "fr" else re.escape(name)
        )
        if re.search(marker_pattern, person_index) is None:
            marker_description = (
                "em dash marker" if language == "fr" else "index entry"
            )
            raise ValueError(
                f"The {language} person index is missing the {marker_description} "
                f"for {name}."
            )

    index_description = (
        "em dash markers in the person index"
        if language == "fr"
        else "person index entries"
    )
    print(
        f"{language} tagged PDF check passed: {pdf_language} and title metadata, "
        "PDF 2.0, "
        f"{role_counts['/L']} L list(s), {role_counts['/LI']} LI item(s), "
        f"{role_counts['/H3']} H3 heading(s), "
        f"{role_counts['/Figure']} figure(s) with alternative text, "
        f"{index_description}, and DisplayDocTitle."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--language", choices=("en", "fr"), default="fr")
    args = parser.parse_args()
    try:
        verify(args.pdf, args.language)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"Tagged PDF check failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
