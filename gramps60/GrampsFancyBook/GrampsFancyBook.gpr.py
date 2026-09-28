"""Gramps 6 report registration."""

# Gramps injects the add-on-aware gettext function as `_` while loading a GPR.

register(
    REPORT,
    id="gramps_fancy_genealogical_book",
    name=_("Gramps Fancy Genealogical Book"),
    description=_(
        "Generate a PDF or static HTML book for the selected reference family. "
        "Exports may include readable private data and information about living "
        "people; confirm that you are authorized to create and share the file."
    ),
    version="0.9.0",
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
