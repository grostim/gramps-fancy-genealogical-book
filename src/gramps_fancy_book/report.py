"""Framework-neutral report entry point for the first milestone."""

from .gramps_adapter import FamilySource
from .normalization import build_book_model
from .traversal import parse_depth_limit


def create_intermediate_model(
    source: FamilySource,
    family_handle: str,
    max_ancestor_depth: int | str | None = None,
    max_descendant_depth: int | str | None = None,
):
    """Select one family and return the shared intermediate editorial model."""
    max_ancestor_depth = parse_depth_limit(max_ancestor_depth)
    max_descendant_depth = parse_depth_limit(max_descendant_depth)
    read_snapshot = getattr(source, "read_snapshot", None)
    if callable(read_snapshot):
        if max_ancestor_depth is None and max_descendant_depth is None:
            snapshot = read_snapshot(family_handle)
        else:
            snapshot = read_snapshot(
                family_handle,
                max_ancestor_depth=max_ancestor_depth,
                max_descendant_depth=max_descendant_depth,
            )
        return build_book_model(snapshot, max_ancestor_depth, max_descendant_depth)
    return build_book_model(source.get_family(family_handle))
