from gramps_fancy_book.domain import Family, Person
from gramps_fancy_book.gramps_adapter import FamilySource
from gramps_fancy_book.renderers.html import render_html
from gramps_fancy_book.renderers.latex import render_latex
from gramps_fancy_book.report import create_intermediate_model


class InMemoryFamilySource(FamilySource):
    def __init__(self, family):
        self.family = family

    def get_family(self, handle):
        assert handle == self.family.handle
        return self.family


def test_select_family_and_build_shared_model():
    family = Family(
        handle="F0001",
        father=Person("I0001", "Jean Dupont"),
        mother=Person("I0002", "Jeanne Martin"),
        children=(Person("I0003", "Paul Dupont"),),
    )

    model = create_intermediate_model(InMemoryFamilySource(family), "F0001")

    assert model.metadata["BOOK_REFERENCE_FAMILY"] == "F0001"
    assert [person.handle for person in model.people] == ["I0001", "I0002", "I0003"]
    assert "F0001" in render_html(model)
    assert "F0001" in render_latex(model)


def test_model_is_json_serializable_shape():
    family = Family(handle="F0002")
    model = create_intermediate_model(InMemoryFamilySource(family), "F0002")

    payload = model.to_dict()
    assert payload["reference_family"]["handle"] == "F0002"
    assert payload["reference_family"]["father"] is None
    assert payload["reference_family"]["children"] == []
    assert payload["people"] == []
    assert payload["families"]["F0002"]["handle"] == "F0002"
    assert payload["events"] == payload["citations"] == payload["media"] == {}
    assert payload["privacy"] == {"contains_private_data": False}
    assert payload["metadata"] == {
        "BOOK_SCHEMA_VERSION": "0.3",
        "BOOK_REFERENCE_FAMILY": "F0002",
    }
