from gramps_fancy_book.consistency import build_consistency_report
from gramps_fancy_book.domain import (
    Attribute,
    BookModel,
    DateValue,
    Event,
    Family,
    ObjectLinks,
    Place,
)


def _event(handle, gramps_id, fact_id, date=None, place_handle=None):
    return Event(
        handle=handle,
        gramps_id=gramps_id,
        type="Birth",
        date=date,
        place_handle=place_handle,
        links=ObjectLinks(attributes=(Attribute("BOOK_FACT_ID", fact_id),)),
    )


def _date(display, start, stop):
    return DateValue(
        display=display,
        sort_value=1,
        modifier=0,
        range=(start, stop),
    )


def _model(events, places=()):
    return BookModel(
        reference_family=Family("family-handle", gramps_id="F0001"),
        events={event.handle: event for event in events},
        places={place.handle: place for place in places},
    )


def test_disjoint_dates_are_confirmed_and_distinct_places_need_review():
    events = [
        _event(
            "event-1900",
            "E0001",
            "birth-of-emile",
            _date("1 Jan 1900", (1900, 1, 1), (1900, 12, 31)),
            "place-lyon",
        ),
        _event(
            "event-1910",
            "E0002",
            " birth-of-emile ",
            _date("1 Jan 1910", (1910, 1, 1), (1910, 12, 31)),
            "place-villeurbanne",
        ),
    ]
    model = _model(
        events,
        (
            Place("place-lyon", name="Lyon"),
            Place("place-villeurbanne", name="Villeurbanne"),
        ),
    )
    original_model = model.to_dict()

    report = build_consistency_report(model)

    assert report["scope"] == {
        "grouping_attribute": "BOOK_FACT_ID",
        "compared_groups": 1,
        "declared_groups": 1,
    }
    assert report["groups"][0]["book_fact_id"] == "birth-of-emile"
    assert report["groups"][0]["event_handles"] == ["event-1900", "event-1910"]
    assert {
        (finding["field"], finding["classification"])
        for finding in report["findings"]
    } == {
        ("date", "confirmed_conflict"),
        ("place", "review_required"),
    }
    date_finding = next(item for item in report["findings"] if item["field"] == "date")
    assert date_finding["values"][0]["range"] == [[1900, 1, 1], [1900, 12, 31]]
    assert date_finding["values"][1]["range"] == [[1910, 1, 1], [1910, 12, 31]]
    place_finding = next(item for item in report["findings"] if item["field"] == "place")
    assert [item["display"] for item in place_finding["values"]] == ["Lyon", "Villeurbanne"]
    assert model.to_dict() == original_model
    assert not model.diagnostics


def test_overlapping_date_ranges_do_not_create_a_conflict():
    model = _model(
        [
            _event(
                "event-a",
                "E0001",
                "same-fact",
                _date("1900–1910", (1900, 1, 1), (1910, 12, 31)),
                "place-same",
            ),
            _event(
                "event-b",
                "E0002",
                "same-fact",
                _date("1910–1920", (1910, 1, 1), (1920, 12, 31)),
                "place-same",
            ),
        ]
    )

    report = build_consistency_report(model)

    assert report["findings"] == []
    assert report["scope"]["compared_groups"] == 1


def test_fact_ids_are_trimmed_but_remain_case_sensitive():
    model = _model(
        [
            _event("event-a", "E0001", "family"),
            _event("event-b", "E0002", " family "),
            _event("event-c", "E0003", "Family"),
        ]
    )

    report = build_consistency_report(model)

    assert report["scope"]["declared_groups"] == 2
    assert report["scope"]["compared_groups"] == 1
    assert [group["book_fact_id"] for group in report["groups"]] == ["family"]
    assert report["groups"][0]["event_handles"] == ["event-a", "event-b"]


def test_ambiguous_fact_ids_are_diagnosed_and_excluded_from_comparison():
    ambiguous = Event(
        handle="event-ambiguous",
        gramps_id="E0003",
        type="Birth",
        links=ObjectLinks(
            attributes=(
                Attribute("BOOK_FACT_ID", "fact-a"),
                Attribute("BOOK_FACT_ID", "fact-b"),
            )
        ),
    )
    model = _model(
        [
            _event("event-a", "E0001", "fact-a"),
            _event("event-b", "E0002", "fact-a"),
            ambiguous,
        ]
    )

    report = build_consistency_report(model)

    assert report["groups"][0]["event_handles"] == ["event-a", "event-b"]
    assert report["findings"] == []
    assert report["diagnostics"] == [
        {
            "code": "ambiguous_book_fact_id",
            "severity": "warning",
            "object_type": "event",
            "handle": "event-ambiguous",
            "message": (
                "Event has multiple distinct BOOK_FACT_ID values and was "
                "excluded from comparisons."
            ),
        }
    ]
    assert not model.diagnostics
