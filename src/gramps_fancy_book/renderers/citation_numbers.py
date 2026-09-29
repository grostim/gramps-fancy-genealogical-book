"""Stable editorial citation numbering shared by book renderers."""

from __future__ import annotations

from collections.abc import Iterable

from ..domain import EditorialBook


def citation_number_map(
    editorial_book: EditorialBook | None,
    *,
    context_order: Iterable[str] | None = None,
) -> dict[str, int]:
    """Number citation entries by first use in the renderer's context order.

    The default preserves the LaTeX book's family-notice then profile order.
    Renderers with another display order may pass their context IDs explicitly.
    """
    if editorial_book is None:
        return {}

    contexts_by_id = {
        profile.profile_id: profile for profile in editorial_book.profiles
    }
    contexts_by_id.update(
        {notice.notice_id: notice for notice in editorial_book.family_notices}
    )
    default_order = tuple(
        notice.notice_id for notice in editorial_book.family_notices
    ) + tuple(profile.profile_id for profile in editorial_book.profiles)
    if context_order is None:
        context_order = default_order

    entries = editorial_book.citation_entries
    entries_by_call = {
        call.call_id: entry
        for entry in entries
        for call in entry.calls
    }
    ordered_entry_ids = []
    seen_entry_ids = set()
    ordered_context_ids = []
    seen_context_ids = set()
    for context_id in context_order:
        if context_id in contexts_by_id and context_id not in seen_context_ids:
            ordered_context_ids.append(context_id)
            seen_context_ids.add(context_id)
    ordered_context_ids.extend(
        context_id for context_id in default_order if context_id not in seen_context_ids
    )
    for context_id in ordered_context_ids:
        context = contexts_by_id[context_id]
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
