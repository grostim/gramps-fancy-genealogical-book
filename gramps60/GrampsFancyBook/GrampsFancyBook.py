"""Gramps report that serializes the selected family to the shared book model."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

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
from gramps_fancy_book.gramps_adapter import GrampsDatabaseAdapter  # noqa: E402
from gramps_fancy_book.normalization import build_book_model  # noqa: E402


class GrampsFancyBookReport(Report):
    """Write a JSON intermediate model for the selected family."""

    def write_report(self) -> None:
        gramps_id = self.options_class.get_reference_family_id()
        try:
            adapter = GrampsDatabaseAdapter(self.database)
            family = adapter.get_family_by_gramps_id(gramps_id)
            model = build_book_model(family)
            output = self.options_class.get_output()
            if not output:
                raise ValueError("No output file was selected")
            Path(output).write_text(
                json.dumps(model.to_dict(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        except Exception as exc:
            raise ReportError(_("Book model export failed"), str(exc)) from exc

        self._custom_output_written = True

    def end_report(self) -> None:
        if not getattr(self, "_custom_output_written", False):
            super().end_report()
