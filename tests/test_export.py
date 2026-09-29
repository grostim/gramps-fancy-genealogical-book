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
    assert json.loads(output.read_text(encoding="utf-8"))["people"][0]["name"] == "Émile"
    assert "Émile" in output.read_text(encoding="utf-8")
    output.write_text("existing output", encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_model_json(model, output)
    assert output.read_text(encoding="utf-8") == "existing output"
    write_model_json(model, output, overwrite=True)
    assert json.loads(output.read_text(encoding="utf-8")) == model.to_dict()
    assert not list(tmp_path.glob(".book-model-*"))


def test_consistency_companion_is_protected_and_replaced_with_model(tmp_path, model):
    output = tmp_path / "model.json"
    companion = tmp_path / "model_consistency.json"
    original_report = {"report_schema_version": "1.0", "findings": []}
    replacement_report = {
        "report_schema_version": "1.0",
        "findings": [{"code": "disjoint_event_date_ranges"}],
    }

    write_model_json(model, output, consistency_report=original_report)
    original_model = output.read_text(encoding="utf-8")
    original_companion = companion.read_text(encoding="utf-8")
    assert json.loads(original_companion) == original_report

    with pytest.raises(FileExistsError):
        write_model_json(model, output, consistency_report=replacement_report)
    assert output.read_text(encoding="utf-8") == original_model
    assert companion.read_text(encoding="utf-8") == original_companion

    write_model_json(
        model,
        output,
        overwrite=True,
        consistency_report=replacement_report,
    )
    assert json.loads(output.read_text(encoding="utf-8")) == model.to_dict()
    assert json.loads(companion.read_text(encoding="utf-8")) == replacement_report

    orphan_companion = tmp_path / "orphan_consistency.json"
    orphan_companion.write_text("previous companion", encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_model_json(
            model,
            tmp_path / "orphan.json",
            consistency_report=original_report,
        )
    assert not (tmp_path / "orphan.json").exists()
    assert orphan_companion.read_text(encoding="utf-8") == "previous companion"


def test_invalid_destination_leaves_existing_files_intact(tmp_path, model):
    invalid = tmp_path / "book.pdf"
    invalid.write_text("original", encoding="utf-8")
    with pytest.raises(ValueError):
        write_model_json(model, invalid, overwrite=True)
    assert invalid.read_text(encoding="utf-8") == "original"
    with pytest.raises(ValueError):
        write_model_json(model, "")
    with pytest.raises(OSError):
        write_model_json(model, tmp_path / "missing" / "file.json")
    assert not list(tmp_path.glob(".book-model-*"))
