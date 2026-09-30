# Troubleshooting

See the [English README](../README.md) for installation and the [French guide](troubleshooting.fr.md) for the translated version.

## The report does not appear in Gramps

Confirm the add-on was extracted with its `GrampsFancyBook/` directory intact into the Gramps 6 user plug-ins directory, then restart Gramps. Look under **Reports → Web Pages**. If the report reports a missing required module, install `mistune>=3,<4` into the same Python environment that launches Gramps Desktop, then restart it.

## The report rejects the selected family

The reference family (F0) must have two known partners. Select a complete couple in the report options. The add-on does not infer an unknown partner from other relationships.

## The output path is rejected or no output appears

The destination directory must already exist. The automatic format selection uses `.pdf` for PDF, `.zip` for the HTML book, and preserves `.json` for the diagnostic snapshot. Choose the matching explicit format and extension if automatic selection is not suitable. Enable **Replace an existing file** only when replacing output is intended; otherwise existing files are preserved.

For a JSON snapshot, the report also writes a separate `<name>_consistency.json` file and may write a neighboring `<name>_media/` folder when images can be converted.

## Images or PDF pages are missing

Image and PDF conversion is optional. Install `Pillow>=10` and `pypdfium2>=4` into the Python environment used by Gramps, then restart Gramps. Missing converters produce diagnostics and omit the affected derivatives. A PDF with a citation URL is kept as a link; an unlinked multipage PDF is retained as a reference rather than rasterized.

## The HTML archive will not open as a local book

Extract the ZIP first and open its `index.html`. The archive is designed to use relative links and work offline after extraction. Keep the archive's directory structure intact when copying it.

## A command-line run exits successfully but appears to have failed

Gramps may return exit code zero even when a report fails. Check that the requested output was created and inspect the report diagnostics. Use the supplied fictional fixture and integration runner when preparing a reproducible report; do not attach a real family export or unredacted logs to an issue.

## PDF generation fails

PDF output requires LuaLaTeX. Install TeX Live and ensure Gramps can find `lualatex` on `PATH`; on macOS the report also checks `/Library/TeX/texbin/lualatex`, the standard BasicTeX/MacTeX link. The application may have a different `PATH` from an interactive shell. If compilation fails, the report will indicate whether LuaLaTeX was unavailable, references failed to stabilize, or the log reported unresolved references or overfull boxes. Use HTML ZIP output when LuaLaTeX is unavailable.

## Gramps Web

Execution in Gramps Web has not been qualified. The add-on and its Python dependencies would need to be installed in the server environment, and there is no validated test instance documented yet.
