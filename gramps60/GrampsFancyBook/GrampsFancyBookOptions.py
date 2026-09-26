"""Minimal Gramps report options for the first milestone."""

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.plug.menu import FamilyOption
from gramps.gen.plug.report import MenuReportOptions

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

    def get_reference_family_id(self) -> str:
        option = self.menu.get_option_by_name("reference_family")
        family_id = option.get_value() if option else None
        if not family_id:
            raise ValueError(_("Select a reference family."))
        return family_id
