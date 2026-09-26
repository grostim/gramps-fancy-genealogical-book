"""Gramps 6 report registration."""

register(
    REPORT,
    id="gramps_fancy_genealogical_book",
    name=_("Gramps Fancy Genealogical Book"),
    description=_("Select a reference family and export a testable book model."),
    version="0.1.0",
    gramps_target_version="6.0",
    status=UNSTABLE,
    fname="GrampsFancyBook.py",
    reportclass="GrampsFancyBookReport",
    optionclass="GrampsFancyBookOptions",
    authors=["Gramps Fancy Genealogical Book contributors"],
    authors_email=[],
    category=CATEGORY_TEXT,
    report_modes=[REPORT_MODE_GUI, REPORT_MODE_CLI],
    require_active=False,
)
