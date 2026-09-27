"""Framework-neutral report entry point for the first milestone."""

from .gramps_adapter import FamilySource
from .normalization import build_book_model


def create_intermediate_model(source: FamilySource, family_handle: str):
    """Select one family and return the shared intermediate editorial model."""
    return build_book_model(source.get_family(family_handle))
