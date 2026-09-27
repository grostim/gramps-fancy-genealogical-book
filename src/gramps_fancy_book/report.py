"""Framework-neutral report entry point for the first milestone."""

from .gramps_adapter import FamilySource
from .normalization import build_book_model


def create_intermediate_model(source: FamilySource, family_handle: str):
    """Select one family and return the shared intermediate editorial model."""
    read_snapshot = getattr(source, "read_snapshot", None)
    if callable(read_snapshot):
        return build_book_model(read_snapshot(family_handle))
    return build_book_model(source.get_family(family_handle))
