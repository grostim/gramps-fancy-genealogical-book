# Declare and inspect versions of the same fact

The consistency report is separate from the book. It compares distinct **Event** objects only when you deliberately give them the same `BOOK_FACT_ID`. It does not match similar events automatically or remove any version from the book.

1. In Gramps, open the first Event object to inspect. On its **Attributes** tab, add a custom attribute type `BOOK_FACT_ID` with a value of your choice, such as `birth-person-42`. Save the event.
2. Open the second Event object describing that same fact. Add an attribute with the same type and **exactly the same value**, then save it. The attribute belongs on the Event objects, not their references from a person or family record.
3. Run **Gramps Fancy Genealogical Book** from **Reports → Web Pages**. Choose the reference family, confirm the privacy option, select **JSON snapshot and consistency report**, and choose a destination such as `family.json` in an existing directory.
4. Open the neighboring `family_consistency.json` file. `groups` lists the compared events; `findings` contains conclusions. An empty `findings` list means this check detected no covered divergence among the compared groups.

In `findings`, `disjoint_event_date_ranges` with `confirmed_conflict` means two normalized Gramps date ranges do not overlap. `different_event_place_references` with `review_required` flags different place references for human review; it does not prove the places are incompatible. Missing, text-only, or otherwise uncomparable dates remain visible in `groups` without a date-conflict conclusion.

`BOOK_FACT_ID` values are case-sensitive, with leading and trailing whitespace ignored. Use a database-wide unique value for each fact. An event with several distinct values is excluded from comparisons and appears in `diagnostics`. The report can contain private data and internal identifiers; share it with the same care as the JSON snapshot.

The UI entry steps are based on Gramps 6.0.8 components; manual validation remains open. See [decisions 005](decisions/005-event-fact-identity.md) and [006](decisions/006-consistency-report.md) for the exact contract.
