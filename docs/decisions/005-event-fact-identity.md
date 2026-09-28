# Decision 005: explicit identity for event fact versions

## Context

The specification requires a separate report for objective date/place contradictions about one fact. It also requires every version to remain visible in the book and forbids merging distinct events by inference. Gramps event objects already have native custom attributes that the project extraction layer preserves.

## Decision

Use the native Gramps event attribute type `BOOK_FACT_ID` to declare that multiple Event objects are versions of the same fact. The value is an arbitrary, database-wide identifier. After trimming surrounding whitespace, values are matched exactly and case-sensitively. Empty values do not create a group.

An event with one distinct non-empty `BOOK_FACT_ID` value belongs to that fact group. Repeated copies of the same value on one event still yield one group membership. If an event carries multiple distinct values, it is ambiguous: exclude that event from contradiction comparisons and emit a technical diagnostic. Events without a valid ID remain independent.

The ID is a grouping key only for the separate date/place contradiction report. It does not merge Event objects, choose a preferred version, suppress citations, or add warnings to the book. Every version remains visible in the book. Similar dates, places, event types, descriptions, citations or participants never imply shared fact identity. `BOOK_FACT_ID` is technical metadata and is not printed as event content.

Gramps’ native event attributes are serialized by the [official XML exporter](https://github.com/gramps-project/gramps/blob/master/gramps/plugins/export/exportxml.py) and allowed for event objects by the [Gramps XML DTD](https://github.com/gramps-project/gramps/blob/master/data/grampsxml.dtd).

## Validation status

The separate report and ambiguous-ID diagnostic are implemented in [Decision 006](006-consistency-report.md). The Gramps 6.0.8 integration fixture loads two native XML Birth events carrying the same `BOOK_FACT_ID` into the add-on export, verifies that they remain separate model events, and checks that the report compares them. The user-interface workflow for entering this attribute in Gramps remains a manual validation item.