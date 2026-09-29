"""Stable editorial citation numbering shared by book renderers."""

from __future__ import annotations

from ..domain import EditorialBook


def citation_number_map(editorial_book: EditorialBook | None) -> dict[str, int]:
    """Number each citation entry in first-use order across the book."""
    if editorial_book is None:
        return {}

    entries = editorial_book.citation_entries
    entries_by_call = {
        call.call_id: entry
        for entry in entries
        for call in entry.calls
    }
    ordered_entry_ids = []
    seen_entry_ids = set()
    for context in (*editorial_book.family_notices, *editorial_book.profiles):
        for call_id in context.citation_call_ids:
            entry = entries_by_call.get(call_id)
            if entry is not None and entry.entry_id not in seen_entry_ids:
                ordered_entry_ids.append(entry.entry_id)
                seen_entry_ids.add(entry.entry_id)
    for entry in entries:
        if entry.entry_id not in seen_entry_ids:
            ordered_entry_ids.append(entry.entry_id)
            seen_entry_ids.add(entry.entry_id)
    return {
        entry_id: number
        for number, entry_id in enumerate(ordered_entry_ids, start=1)
    }
