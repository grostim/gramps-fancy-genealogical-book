"""Minimal HTML renderer proving the shared model contract."""

from html import escape

from ..domain import BookModel


def render_html(model: BookModel) -> str:
    family = model.reference_family
    return (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8"><title>'
        f"{escape(family.handle)}</title></head><body>\n"
        f"<h1>{escape(family.handle)}</h1>\n"
        f"<p>{len(model.people)} people in the intermediate model.</p>\n"
        "</body></html>\n"
    )
