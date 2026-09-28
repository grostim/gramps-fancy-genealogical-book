"""Build a separate report for explicitly linked versions of the same event fact."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Any

from .conventions import BOOK_FACT_ID
from .domain import BookModel, DateValue, Event


_REPORT_SCHEMA_VERSION = "1.0"
_TEXT_ONLY_MODIFIER = 6


def build_consistency_report(model: BookModel) -> dict[str, object]:
    """Return JSON-safe findings without changing events or book diagnostics."""
    events_by_fact: dict[str, list[Event]] = defaultdict(list)
    diagnostics: list[dict[str, str]] = []

    for event in sorted(model.events.values(), key=lambda item: (item.gramps_id, item.handle)):
        fact_ids = {
            attribute.value.strip()
            for attribute in event.links.attributes
            if attribute.type == BOOK_FACT_ID and attribute.value.strip()
        }
        if len(fact_ids) > 1:
            diagnostics.append(
                {
                    "code": "ambiguous_book_fact_id",
                    "severity": "warning",
                    "object_type": "event",
                    "handle": event.handle,
                    "message": (
                        "Event has multiple distinct BOOK_FACT_ID values and was "
                        "excluded from comparisons."
                    ),
                }
            )
            continue
        if fact_ids:
            events_by_fact[next(iter(fact_ids))].append(event)

    groups: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    declared_group_count = 0
    compared_group_count = 0

    for fact_id in sorted(events_by_fact):
        events = sorted(events_by_fact[fact_id], key=lambda item: (item.gramps_id, item.handle))
        declared_group_count += 1
        if len(events) < 2:
            continue
        compared_group_count += 1

        event_summaries = [_event_summary(event, model) for event in events]
        groups.append(
            {
                "book_fact_id": fact_id,
                "event_handles": [event.handle for event in events],
                "events": event_summaries,
            }
        )

        for left, right in combinations(events, 2):
            left_range = _date_range(left.date)
            right_range = _date_range(right.date)
            if left_range is not None and right_range is not None:
                if left_range[1] < right_range[0] or right_range[1] < left_range[0]:
                    findings.append(
                        {
                            "code": "disjoint_event_date_ranges",
                            "classification": "confirmed_conflict",
                            "field": "date",
                            "book_fact_id": fact_id,
                            "event_handles": [left.handle, right.handle],
                            "values": [
                                {
                                    "event_handle": left.handle,
                                    "display": left.date.display,
                                    "range": _json_range(left_range),
                                },
                                {
                                    "event_handle": right.handle,
                                    "display": right.date.display,
                                    "range": _json_range(right_range),
                                },
                            ],
                        }
                    )

        place_values: dict[str, list[Event]] = defaultdict(list)
        for event in events:
            if event.place_handle:
                place_values[event.place_handle].append(event)
        if len(place_values) > 1:
            findings.append(
                {
                    "code": "different_event_place_references",
                    "classification": "review_required",
                    "field": "place",
                    "book_fact_id": fact_id,
                    "event_handles": [event.handle for event in events if event.place_handle],
                    "values": [
                        {
                            "place_handle": place_handle,
                            "display": _place_display(place_handle, model),
                            "event_handles": [event.handle for event in place_events],
                        }
                        for place_handle, place_events in sorted(place_values.items())
                    ],
                }
            )

    findings.sort(
        key=lambda item: (
            item["book_fact_id"],
            item["field"],
            item["code"],
            tuple(item["event_handles"]),
        )
    )
    return {
        "report_schema_version": _REPORT_SCHEMA_VERSION,
        "report_type": "event_fact_consistency",
        "reference_family": {
            "handle": model.reference_family.handle,
            "gramps_id": model.reference_family.gramps_id,
        },
        "scope": {
            "grouping_attribute": BOOK_FACT_ID,
            "compared_groups": compared_group_count,
            "declared_groups": declared_group_count,
        },
        "groups": groups,
        "findings": findings,
        "diagnostics": diagnostics,
    }


def _event_summary(event: Event, model: BookModel) -> dict[str, Any]:
    return {
        "handle": event.handle,
        "gramps_id": event.gramps_id,
        "type": event.type,
        "description": event.description,
        "date": event.date.display if event.date else "",
        "date_range": _json_range(_date_range(event.date)) if _date_range(event.date) else None,
        "place_handle": event.place_handle,
        "place": _place_display(event.place_handle, model) if event.place_handle else "",
    }


def _place_display(place_handle: str, model: BookModel) -> str:
    place = model.places.get(place_handle)
    if place is None:
        return ""
    return place.name or place.title


def _date_range(date: DateValue | None) -> tuple[tuple[int, int, int], tuple[int, int, int]] | None:
    """Read Gramps' Gregorian min/max range while rejecting uncomparable dates."""
    if date is None or date.sort_value is None or date.modifier == _TEXT_ONLY_MODIFIER:
        return None
    value = date.range
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return None
    bounds = []
    for endpoint in value:
        if not isinstance(endpoint, (list, tuple)) or len(endpoint) < 3:
            return None
        if any(isinstance(part, bool) or not isinstance(part, int) for part in endpoint[:3]):
            return None
        bounds.append(tuple(endpoint[:3]))
    start, stop = bounds
    if start > stop:
        return None
    return start, stop


def _json_range(
    value: tuple[tuple[int, int, int], tuple[int, int, int]] | None,
) -> list[list[int]] | None:
    if value is None:
        return None
    return [list(value[0]), list(value[1])]
