# Design reference — specification v1.1

This file records the implementation baseline extracted from the approved design discussion.

## Scope

The plugin, named **Gramps Fancy Genealogical Book**, will generate a family genealogical book from Gramps data. It must support a shared editorial model with LaTeX/PDF and HTML outputs, while respecting Gramps permissions and never bypassing access controls.

## First milestone

The first milestone is intentionally limited to a clean installable foundation:

- select a reference family;
- define stable contracts for Gramps extraction and normalization;
- produce a testable intermediate model;
- keep renderer implementations behind the common model;
- provide packaging, tests, CI, and bilingual documentation.

The complete genealogy algorithms, pagination, sources, media handling, and polished mockup fidelity are subsequent milestones.

## Design references

The structural family-book mockup and the events-and-sources mockup are visual references for typography, page composition, navigation, individual profiles, events, sources, and appendices. They are inspiration and validation aids; the written specification remains authoritative when a future implementation choice conflicts with a mockup.

## Naming

Code, variables, technical metadata, and Gramps tags use English identifiers. Publication tags use `BOOK_*`, including `BOOK_PUBLICATION`, `BOOK_PROFILE`, `BOOK_EXCLUDE`, and `BOOK_FEATURED`. Display labels remain translatable.

