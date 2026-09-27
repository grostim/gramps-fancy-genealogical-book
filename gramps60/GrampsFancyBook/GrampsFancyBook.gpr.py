"""Gramps 6 report registration."""

register(
    REPORT,
    id="gramps_fancy_genealogical_book",
    name=_("Gramps Fancy Genealogical Book"),
    description=_("Select a reference family and export a normalized book-data snapshot."),
    version="0.4.0",
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
    require_active=False,
)
