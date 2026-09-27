import json

import pytest

from gramps_fancy_book.domain import Family, Person
from gramps_fancy_book.export import write_model_json
from gramps_fancy_book.normalization import build_book_model


@pytest.fixture
def model():
    return build_book_model(Family("family-handle", Person("person-handle", "Émile", "I1")))


def test_unicode_export_and_explicit_replacement(tmp_path, model):
    output = tmp_path / "model.json"
    write_model_json(model, output)
    assert json.loads(output.read_text())["people"][0]["name"] == "Émile"
    assert "Émile" in output.read_text()
    output.write_text("existing output")
    with pytest.raises(FileExistsError):
        write_model_json(model, output)
    assert output.read_text() == "existing output"
    write_model_json(model, output, overwrite=True)
    assert json.loads(output.read_text()) == model.to_dict()
    assert not list(tmp_path.glob(".book-model-*"))


def test_invalid_destination_leaves_existing_files_intact(tmp_path, model):
    invalid = tmp_path / "book.pdf"
    invalid.write_text("original")
    with pytest.raises(ValueError):
        write_model_json(model, invalid, overwrite=True)
    assert invalid.read_text() == "original"
    with pytest.raises(ValueError):
        write_model_json(model, "")
    with pytest.raises(OSError):
        write_model_json(model, tmp_path / "missing" / "file.json")
    assert not list(tmp_path.glob(".book-model-*"))
