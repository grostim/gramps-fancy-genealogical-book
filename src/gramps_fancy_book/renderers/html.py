"""Minimal HTML renderer proving the shared model contract."""

from ..domain import BookModel


def render_html(model: BookModel) -> str:
    family = model.reference_family
    return (
        "<!doctype html>\n"
        "<html lang=\"en\"><head><meta charset=\"utf-8\"><title>"
        f"{family.handle}</title></head><body>\n"
        f"<h1>{family.handle}</h1>\n"
        f"<p>{len(model.people)} people in the intermediate model.</p>\n"
        "</body></html>\n"
    )

