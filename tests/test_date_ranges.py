from gramps_fancy_book.date_ranges import stable_order_by_date_range
from gramps_fancy_book.domain import DateValue, Event, EventReference
from gramps_fancy_book.editorial import _chronological_event_refs


def _range(start, stop=None):
    return (start, stop or start)


def _date(display, start=None, stop=None, *, sort_value=1, modifier=0):
    return DateValue(
        display=display,
        sort_value=sort_value,
        modifier=modifier,
        range=(start, stop or start) if start is not None else None,
    )


def test_stable_order_groups_transitive_overlaps_and_puts_uncomparable_last():
    items = (
        (_range((1907, 1, 1), (1910, 1, 1)), (0, "chain-c"), "chain-c"),
        (_range((1890, 1, 1)), (1, "early"), "early"),
        (_range((1900, 1, 1), (1904, 1, 1)), (2, "chain-a"), "chain-a"),
        (None, (3, "unknown"), "unknown"),
        (_range((1903, 1, 1), (1908, 1, 1)), (4, "chain-b"), "chain-b"),
    )

    assert stable_order_by_date_range(items) == (
        "early",
        "chain-c",
        "chain-a",
        "chain-b",
        "unknown",
    )


def test_event_chronology_uses_ranges_and_keeps_source_order_when_they_overlap():
    references = tuple(
        EventReference(event_handle=handle)
        for handle in ("point", "broad", "early", "late", "unknown", "text-only")
    )
    events = {
        # Deliberately inconsistent scalar sort values ensure chronology uses bounds.
        "point": Event(
            handle="point",
            type="Residence",
            date=_date("15 June 1900", (1900, 6, 15), sort_value=6000),
        ),
        "broad": Event(
            handle="broad",
            type="Residence",
            date=_date("1900", (1900, 1, 1), (1900, 12, 31), sort_value=100),
        ),
        "early": Event(
            handle="early",
            type="Residence",
            date=_date("1899", (1899, 1, 1), (1899, 12, 31), sort_value=5000),
        ),
        "late": Event(
            handle="late",
            type="Residence",
            date=_date("1902", (1902, 1, 1), (1902, 12, 31), sort_value=0),
        ),
        "unknown": Event(handle="unknown", type="Residence"),
        "text-only": Event(
            handle="text-only",
            type="Residence",
            date=_date(
                "before the war",
                (1890, 1, 1),
                (1899, 12, 31),
                modifier=6,
            ),
        ),
    }

    assert [
        reference.event_handle
        for reference in _chronological_event_refs(references, events)
    ] == ["early", "point", "broad", "late", "unknown", "text-only"]
