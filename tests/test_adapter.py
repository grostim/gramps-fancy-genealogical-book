from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from gramps_fancy_book.gramps_adapter import GrampsDatabaseAdapter
from gramps_fancy_book.normalization import build_book_model


def make_database():
    family = Mock()
    family.get_handle.return_value = "family-handle"
    family.get_gramps_id.return_value = "F0042"
    family.get_father_handle.return_value = "parent-handle"
    family.get_mother_handle.return_value = None
    family.get_child_ref_list.return_value = [SimpleNamespace(ref="child-handle")]
    parent = Mock()
    parent.get_primary_name.return_value.get_name.return_value = "Exemple, Émile"
    parent.get_gramps_id.return_value = "I0007"
    child = Mock()
    child.get_primary_name.return_value.get_name.return_value = "Exemple, Camille"
    child.get_gramps_id.return_value = "I0008"
    db = Mock()
    db.get_family_from_gramps_id.return_value = family
    db.get_family_from_handle.return_value = family
    db.get_person_from_handle.side_effect = {"parent-handle": parent, "child-handle": child}.get
    return db


def test_ids_handles_and_unknown_parent_are_preserved():
    db = make_database()
    family = GrampsDatabaseAdapter(db).get_family_by_gramps_id("F0042")
    db.get_family_from_handle.assert_called_once_with("family-handle")
    assert family.gramps_id == "F0042"
    assert family.mother is None
    assert [p.gramps_id for p in build_book_model(family).people] == ["I0007", "I0008"]
    assert family.father.name == "Exemple, Émile"


def test_dangling_reference_is_reported_instead_of_silently_omitted():
    db = make_database()
    db.get_person_from_handle.side_effect = lambda handle: None
    with pytest.raises(LookupError, match="parent-handle"):
        GrampsDatabaseAdapter(db).get_family_by_gramps_id("F0042")


def test_nonexistent_family_and_empty_selection():
    db = make_database()
    db.get_family_from_gramps_id.return_value = None
    with pytest.raises(LookupError, match="F9999"):
        GrampsDatabaseAdapter(db).get_family_by_gramps_id("F9999")
    with pytest.raises(ValueError, match="Select"):
        GrampsDatabaseAdapter(db).get_family_by_gramps_id("")
