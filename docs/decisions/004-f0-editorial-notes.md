# Decision 004: F0 editorial notes

## Context

The specification stores the title, subtitle, introduction, dedication, author and publication date in notes attached to the selected central family (F0). `BOOK_PUBLICATION` remains the publication gate. The proposed role names are plugin conventions, not built-in Gramps note types.

## Decision

Use native Gramps tags to identify the six roles: `BOOK_TITLE`, `BOOK_SUBTITLE`, `BOOK_INTRODUCTION`, `BOOK_DEDICATION`, `BOOK_AUTHOR` and `BOOK_PUBLICATION_DATE`. A role note must also carry `BOOK_PUBLICATION` and be linked directly to the selected family. Notes with matching tags elsewhere in the database do not apply.

For each role, keep the first valid note in the family’s note-link order. If a note has multiple role tags, omit it and emit a warning diagnostic. If more than one valid note supplies the same role, keep the first and emit a warning for each later note. A role note without `BOOK_PUBLICATION` or with empty text is omitted with a warning. Role-tagged notes are excluded from the F0 family notice so they do not also appear as ordinary notes there; the same shared note can still appear in another linked context.

The title and subtitle notes replace the cover’s fallback text. The couple’s names remain visible on the cover. Author and publication date notes are shown on the cover. Dedication and introduction notes render, in that order, on separate pages before the contents. Missing role notes are omitted, except that the existing fallback title and couple-name subtitle remain. No publication date is inferred from genealogical dates.

## Validation status

The selector and both renderers use the six role notes. The Gramps 6 native CLI integration fixture exercises all roles, verifies the family-link scope, and checks the duplicate, ambiguous, unpublished and empty-note diagnostics. It checks that each valid role is rendered (the HTML document title also repeats the cover title), that dedication precedes introduction, and that role notes do not reappear in F0's ordinary family notice. These checks do not exercise data entry in the Gramps interface or constitute visual acceptance of the compiled PDF; both remain to be qualified manually.
