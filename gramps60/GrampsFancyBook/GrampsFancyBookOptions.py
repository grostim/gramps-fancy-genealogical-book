"""Minimal Gramps report options for the first milestone."""

from pathlib import Path

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.plug.menu import (
    BooleanOption,
    DestinationOption,
    EnumeratedListOption,
    FamilyOption,
    StringOption,
)
from gramps.gen.plug.report import MenuReportOptions

from gramps_fancy_book.book_language import resolve_book_language
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
        book_language = EnumeratedListOption(_("Book language"), "auto")
        book_language.add_item("auto", _("Use Gramps language"))
        book_language.add_item("fr", _("French"))
        book_language.add_item("en", _("English"))
        book_language.set_help(
            _(
                "Automatic mode follows the language configured in Gramps. If that language is not supported, the book uses English."
            )
        )
        menu.add_option(_("Book"), "book_language", book_language)

        output_format = EnumeratedListOption(_("Output format"), "auto")
        output_format.add_item(
            "auto", _("Automatic (use destination extension)")
        )
        output_format.add_item("html_zip", _("HTML book (ZIP archive)"))
        output_format.add_item("pdf", _("PDF book (LuaLaTeX)"))
        output_format.add_item(
            "json_snapshot", _("JSON snapshot (development diagnostics)")
        )
        output_format.set_help(
            _("Automatic mode uses .pdf for PDF books, .zip for HTML books, and .json for diagnostic snapshots.")
        )
        menu.add_option(_("Book"), "output_format", output_format)

        extended_pdf_compilation = BooleanOption(
            _("Allow extended PDF compilation (up to 30 minutes)"), False
        )
        extended_pdf_compilation.set_help(
            _(
                "Use this for long PDF books when the standard three-minute limit expires. "
                "Each LuaLaTeX pass is limited to ten minutes."
            )
        )
        menu.add_option(_("Book"), "extended_pdf_compilation", extended_pdf_compilation)

        privacy_acknowledged = BooleanOption(
            _(
                "I understand this export may include private data and information about living people."
            ),
            False,
        )
        privacy_acknowledged.set_help(
            _(
                "Gramps access permissions remain in force, but this report does not filter or anonymize readable data. Confirm that you are authorized to create and share this export."
            )
        )
        menu.add_option(_("Privacy"), "privacy_acknowledged", privacy_acknowledged)

        destination = DestinationOption(_("Output file"), "")
        # The report supports multiple formats; get_destination() adds the
        # format-specific extension when the selected path has no suffix.
        destination.set_extension("")
        destination.set_help(
            _(
                "Automatic mode uses .pdf for PDF, .zip for HTML, or .json for the development "
                "snapshot."
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
        try:
            return parse_depth_limit(
                self.menu.get_option_by_name("max_ancestor_depth").get_value()
            )
        except ValueError as error:
            raise ValueError(
                _("Maximum ancestry generations must be a non-negative integer or 'unlimited'.")
            ) from error

    def get_max_descendant_depth(self) -> int | None:
        try:
            return parse_depth_limit(
                self.menu.get_option_by_name("max_descendant_depth").get_value()
            )
        except ValueError as error:
            raise ValueError(
                _("Maximum descendant generations must be a non-negative integer or 'unlimited'.")
            ) from error

    def get_book_language(self) -> str:
        selected = self.menu.get_option_by_name("book_language").get_value()
        configured = getattr(glocale, "language", None)
        if isinstance(configured, (tuple, list)):
            configured = configured[0] if configured else None
        return resolve_book_language(selected, gramps_language=configured)

    def get_output_format(self) -> str:
        output_format = self.menu.get_option_by_name("output_format").get_value()
        if output_format != "auto":
            return output_format

        destination = self.menu.get_option_by_name("destination").get_value()
        suffix = Path(destination or "").suffix.casefold()
        if suffix == ".pdf":
            return "pdf"
        if suffix == ".json":
            return "json_snapshot"
        return "html_zip"

    def get_extended_pdf_compilation(self) -> bool:
        return bool(self.menu.get_option_by_name("extended_pdf_compilation").get_value())

    def get_destination(self) -> str:
        output_format = self.get_output_format()
        extension = {
            "html_zip": ".zip",
            "pdf": ".pdf",
            "json_snapshot": ".json",
        }.get(output_format)
        if extension is None:
            raise ValueError(_("Select a supported output format."))

        value = self.menu.get_option_by_name("destination").get_value()
        if not str(value or "").strip():
            return ""
        output = Path(value).expanduser()
        if not output.suffix:
            output = output.with_suffix(extension)
        return str(output)

    def get_overwrite(self) -> bool:
        return self.menu.get_option_by_name("overwrite").get_value()

    def get_privacy_acknowledged(self) -> bool:
        return bool(self.menu.get_option_by_name("privacy_acknowledged").get_value())

    def load_previous_values(self) -> None:
        super().load_previous_values()
        option = self.menu.get_option_by_name("privacy_acknowledged")
        if option is not None:
            # An earlier acknowledgement must not carry over to a new export.
            option.set_value(False)
            self.options_dict["privacy_acknowledged"] = False

    def get_subject(self) -> str:
        return self.menu.get_option_by_name("reference_family").get_value()
