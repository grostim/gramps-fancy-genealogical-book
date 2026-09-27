"""Gramps report that serializes the selected family to the shared book model."""

from __future__ import annotations

import os
import sys

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

from gramps_fancy_book.export import write_model_json  # noqa: E402
from gramps_fancy_book.gramps_adapter import GrampsDatabaseAdapter  # noqa: E402
from gramps_fancy_book.normalization import build_book_model  # noqa: E402


class GrampsFancyBookReport(Report):
    """Write a JSON intermediate model for the selected family."""

    def write_report(self) -> None:
        try:
            gramps_id = self.options_class.get_reference_family_id()
            adapter = GrampsDatabaseAdapter(self.database)
            snapshot = adapter.read_snapshot_by_gramps_id(gramps_id)
            family = snapshot.reference_family
            if family.father is None or family.mother is None:
                raise ValueError(_("The reference family must have two known partners."))
            model = build_book_model(snapshot)
            write_model_json(
                model,
                self.options_class.get_destination(),
                overwrite=self.options_class.get_overwrite(),
            )
        except FileExistsError as exc:
            raise ReportError(
                _("Output file already exists"),
                _("Choose another JSON output file or enable 'Replace an existing file'."),
            ) from exc
        except (LookupError, ValueError, OSError) as exc:
            raise ReportError(_("Book model export failed"), str(exc)) from exc
