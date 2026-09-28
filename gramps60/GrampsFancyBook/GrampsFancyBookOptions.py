"""Minimal Gramps report options for the first milestone."""

from gramps.gen.const import GRAMPS_LOCALE as glocale
from pathlib import Path

from gramps.gen.plug.menu import (
    BooleanOption,
    DestinationOption,
    EnumeratedListOption,
    FamilyOption,
    StringOption,
)
from gramps.gen.plug.report import MenuReportOptions

from gramps_fancy_book.traversal import parse_depth_limit

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


class GrampsFancyBookOptions(MenuReportOptions):
    def __init__(self, name, database) -> None:
        self._database = database
        super().__init__(name, database)

    def add_menu_options(self, menu) -> None:
        menu.add_option(
            _("Book"),
            "reference_family",
            FamilyOption(_("Reference family")),
        )
        menu.add_option(
            _("Book"),
            "max_ancestor_depth",
            StringOption(_("Maximum ancestry generations ('unlimited' or a number)"), "unlimited"),
        )
        menu.add_option(
            _("Book"),
            "max_descendant_depth",
            StringOption(_("Maximum descendant generations ('unlimited' or a number)"), "unlimited"),
        )
        output_format = EnumeratedListOption(_("Output format"), "html_zip")
        output_format.add_item("html_zip", _("HTML book (ZIP archive)"))
        output_format.add_item(
            "json_snapshot", _("JSON snapshot (development diagnostics)")
        )
        output_format.set_help(
            _("The JSON snapshot is a development aid; use HTML ZIP for a book.")
        )
        menu.add_option(_("Book"), "output_format", output_format)

        destination = DestinationOption(_("Output file"), "")
        destination.set_extension("zip")
        destination.set_help(
            _(
                "Use a .zip destination for HTML, or a .json destination "
                "for the development snapshot."
            )
        )
        menu.add_option(_("Book"), "destination", destination)
        menu.add_option(_("Book"), "overwrite", BooleanOption(_("Replace an existing file"), False))

    def get_reference_family_id(self) -> str:
        option = self.menu.get_option_by_name("reference_family")
        family_id = option.get_value() if option else None
        if not family_id:
            raise ValueError(_("Select a reference family."))
        return family_id

    def get_max_ancestor_depth(self) -> int | None:
        return parse_depth_limit(self.menu.get_option_by_name("max_ancestor_depth").get_value())

    def get_max_descendant_depth(self) -> int | None:
        return parse_depth_limit(self.menu.get_option_by_name("max_descendant_depth").get_value())

    def get_output_format(self) -> str:
        return self.menu.get_option_by_name("output_format").get_value()

    def get_destination(self) -> str:
        output_format = self.get_output_format()
        extension = {
            "html_zip": ".zip",
            "json_snapshot": ".json",
        }.get(output_format)
        if extension is None:
            raise ValueError(_("Select a supported output format."))

        value = self.menu.get_option_by_name("destination").get_value()
        if not str(value or "").strip():
            return ""
        output = Path(value).expanduser()
        if output.suffix.casefold() in {".zip", ".json"} or not output.suffix:
            output = output.with_suffix(extension)
        return str(output)

    def get_overwrite(self) -> bool:
        return self.menu.get_option_by_name("overwrite").get_value()

    def get_subject(self) -> str:
        return self.menu.get_option_by_name("reference_family").get_value()
