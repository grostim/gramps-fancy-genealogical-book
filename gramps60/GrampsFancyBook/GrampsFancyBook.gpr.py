"""Gramps 6 report registration."""

from gramps.gen.const import GRAMPS_LOCALE as glocale

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


register(
    REPORT,
    id="gramps_fancy_genealogical_book",
    name=_("Gramps Fancy Genealogical Book"),
    description=_("Generate a static HTML book archive for the selected reference family."),
    version="0.8.0",
    gramps_target_version="6.0",
    # UNSTABLE add-ons are hidden by release builds of Gramps.
    status=EXPERIMENTAL,
    fname="GrampsFancyBook.py",
    reportclass="GrampsFancyBookReport",
    optionclass="GrampsFancyBookOptions",
    authors=["Gramps Fancy Genealogical Book contributors"],
    authors_email=[],
    # Use the native custom-output lifecycle, without a PDF/ODT document backend.
    category=CATEGORY_WEB,
    report_modes=[REPORT_MODE_GUI, REPORT_MODE_CLI],
    requires_mod=["mistune"],
    require_active=False,
)
