"""Comparable Gramps date ranges and deterministic chronological ordering."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

from .domain import DateValue

DatePoint = tuple[int, int, int]
DateRange = tuple[DatePoint, DatePoint]
_TEXT_ONLY_MODIFIER = 6

T = TypeVar("T")


def comparable_date_range(date: DateValue | None) -> DateRange | None:
    """Return Gramps' comparable Gregorian bounds without inventing precision."""
    if date is None or date.sort_value is None or date.modifier == _TEXT_ONLY_MODIFIER:
        return None
    value = date.range
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return None
    bounds: list[DatePoint] = []
    for endpoint in value:
        if not isinstance(endpoint, (list, tuple)) or len(endpoint) < 3:
            return None
        if any(
            isinstance(part, bool) or not isinstance(part, int)
            for part in endpoint[:3]
        ):
            return None
        bounds.append(tuple(endpoint[:3]))
    start, stop = bounds
    if start > stop:
        return None
    return start, stop


def stable_order_by_date_range(
    items: Iterable[tuple[DateRange | None, tuple[object, ...], T]],
) -> tuple[T, ...]:
    """Sort disjoint intervals chronologically and preserve order when they overlap.

    Overlap is transitive for this ordering: if A overlaps B and B overlaps C,
    the three entries stay in one ambiguity group even when A and C are disjoint.
    Such a group keeps its caller-provided stable fallback order. Uncomparable
    dates follow all dated entries and use the same stable fallback ordering.
    """
    dated: list[tuple[DateRange, tuple[object, ...], int, T]] = []
    undated: list[tuple[tuple[object, ...], int, T]] = []
    for position, (date_range, fallback, item) in enumerate(items):
        if date_range is None:
            undated.append((fallback, position, item))
        else:
            dated.append((date_range, fallback, position, item))

    dated.sort(key=lambda entry: (entry[0][0], entry[0][1], entry[1], entry[2]))
    ordered: list[T] = []
    overlap_group: list[tuple[DateRange, tuple[object, ...], int, T]] = []
    group_stop: DatePoint | None = None

    def flush_overlap_group() -> None:
        overlap_group.sort(key=lambda entry: (entry[1], entry[2]))
        ordered.extend(entry[3] for entry in overlap_group)
        overlap_group.clear()

    for entry in dated:
        date_range = entry[0]
        if group_stop is None or date_range[0] <= group_stop:
            overlap_group.append(entry)
            group_stop = (
                date_range[1]
                if group_stop is None
                else max(group_stop, date_range[1])
            )
        else:
            flush_overlap_group()
            overlap_group.append(entry)
            group_stop = date_range[1]

    if overlap_group:
        flush_overlap_group()

    undated.sort(key=lambda entry: (entry[0], entry[1]))
    ordered.extend(entry[2] for entry in undated)
    return tuple(ordered)
