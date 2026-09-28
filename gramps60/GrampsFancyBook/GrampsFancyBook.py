"""Gramps report that serializes the selected family to the shared book model."""

from __future__ import annotations

import os
import sys
import tempfile

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import ReportError
from gramps.gen.plug.report import Report

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext

_ADDON_DIR = os.path.dirname(os.path.abspath(__file__))
if _ADDON_DIR not in sys.path:
    sys.path.insert(0, _ADDON_DIR)

from GrampsFancyBookOptions import GrampsFancyBookOptions  # noqa: E402,F401

from gramps_fancy_book.consistency import build_consistency_report  # noqa: E402
from gramps_fancy_book.export import (  # noqa: E402
    media_asset_directory_name,
    media_asset_staging_directory,
    write_model_json,
)
from gramps_fancy_book.gramps_adapter import GrampsDatabaseAdapter  # noqa: E402
from gramps_fancy_book.media import prepare_editorial_media  # noqa: E402
from gramps_fancy_book.normalization import build_book_model  # noqa: E402
from gramps_fancy_book.renderers.html_archive import (  # noqa: E402
    validate_html_archive_destination,
    write_html_archive,
)
from gramps_fancy_book.renderers.latex_pdf import (  # noqa: E402
    LatexCompilationError,
    LatexCompilerUnavailable,
    validate_latex_pdf_destination,
    write_latex_pdf,
)


class GrampsFancyBookReport(Report):
    """Write an HTML book archive or a development JSON snapshot."""

    def write_report(self) -> None:
        try:
            output_format = self.options_class.get_output_format()
            gramps_id = self.options_class.get_reference_family_id()
            max_ancestor_depth = self.options_class.get_max_ancestor_depth()
            max_descendant_depth = self.options_class.get_max_descendant_depth()
            destination = self.options_class.get_destination()
            overwrite = self.options_class.get_overwrite()

            adapter = GrampsDatabaseAdapter(self.database)
            snapshot = adapter.read_snapshot_by_gramps_id(
                gramps_id,
                max_ancestor_depth=max_ancestor_depth,
                max_descendant_depth=max_descendant_depth,
            )
            family = snapshot.reference_family
            if family.father is None or family.mother is None:
                raise ValueError(_("The reference family must have two known partners."))
            model = build_book_model(
                snapshot,
                max_ancestor_depth=max_ancestor_depth,
                max_descendant_depth=max_descendant_depth,
            )

            if output_format == "html_zip":
                html_destination = validate_html_archive_destination(
                    destination, overwrite=overwrite
                )
                with tempfile.TemporaryDirectory(
                    prefix=".book-html-media-stage-",
                    dir=html_destination.parent,
                ) as asset_staging:
                    prepare_editorial_media(
                        self.database,
                        model,
                        "media",
                        asset_staging,
                    )
                    write_html_archive(
                        model,
                        html_destination,
                        media_asset_directory=asset_staging,
                        overwrite=overwrite,
                    )
            elif output_format == "pdf":
                pdf_destination = validate_latex_pdf_destination(
                    destination, overwrite=overwrite
                )
                with tempfile.TemporaryDirectory(
                    prefix=".book-pdf-media-stage-",
                    dir=pdf_destination.parent,
                ) as asset_staging:
                    prepare_editorial_media(
                        self.database,
                        model,
                        "media",
                        asset_staging,
                    )
                    write_latex_pdf(
                        model,
                        pdf_destination,
                        media_asset_directory=asset_staging,
                        overwrite=overwrite,
                    )
            elif output_format == "json_snapshot":
                consistency_report = build_consistency_report(model)
                with media_asset_staging_directory(
                    destination,
                    overwrite=overwrite,
                    include_consistency_report=True,
                ) as asset_staging:
                    prepare_editorial_media(
                        self.database,
                        model,
                        media_asset_directory_name(destination),
                        asset_staging,
                    )
                    write_model_json(
                        model,
                        destination,
                        overwrite=overwrite,
                        media_asset_staging=asset_staging,
                        consistency_report=consistency_report,
                    )
            else:
                raise ValueError(_("Select a supported output format."))
        except FileExistsError as exc:
            raise ReportError(
                _("Output already exists"),
                _("Choose another destination or enable 'Replace an existing file'."),
            ) from exc
        except LatexCompilerUnavailable as exc:
            raise ReportError(
                _("PDF output unavailable"),
                _("LuaLaTeX is required to produce a PDF. Install TeX Live and make lualatex available on PATH."),
            ) from exc
        except LatexCompilationError as exc:
            message_id = {
                "compile": "LuaLaTeX could not compile the selected book.",
                "timeout": "LuaLaTeX compilation timed out.",
                "references_unstable": "PDF references did not stabilize after five compilation passes.",
                "layout_warnings": "PDF compilation reported unresolved references or overfull boxes.",
                "missing_pdf": "LuaLaTeX completed without producing a PDF file.",
                "missing_auxiliary_files": "PDF compilation did not produce auxiliary files required to resolve references.",
                "missing_log": "LuaLaTeX did not produce a compilation log.",
            }.get(exc.reason, "LuaLaTeX could not produce a valid PDF.")
            raise ReportError(_("PDF generation failed"), _(message_id)) from exc
        except (LookupError, ValueError, OSError) as exc:
            raise ReportError(_("Book generation failed"), str(exc)) from exc
