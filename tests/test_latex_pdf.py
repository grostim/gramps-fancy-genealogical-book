from gramps_fancy_book.domain import BookModel, EditorialMediaArtifact, Family
from gramps_fancy_book.renderers import latex_pdf


def test_pdf_writer_stages_prepared_media_assets(tmp_path, monkeypatch):
    cache_key = "a" * 64
    payload = b"prepared PNG bytes"
    asset_directory = tmp_path / "staged-media"
    asset_directory.mkdir()
    (asset_directory / f"{cache_key}.png").write_bytes(payload)
    model = BookModel(
        reference_family=Family(handle="family-1"),
        media_artifacts=[
            EditorialMediaArtifact(
                media_handle="media-1",
                rectangle=None,
                action="reproduce",
                cache_key=cache_key,
                asset_path=f"family_media/{cache_key}.png",
            )
        ],
    )

    monkeypatch.setattr(latex_pdf.shutil, "which", lambda _: "/fake/lualatex")

    def compile_pdf(compiler, work_directory):
        assert compiler == "/fake/lualatex"
        assert (work_directory / "media" / f"{cache_key}.png").read_bytes() == payload
        (work_directory / "book.pdf").write_bytes(b"%PDF-test")

    monkeypatch.setattr(latex_pdf, "_compile_latex", compile_pdf)
    output = tmp_path / "book.pdf"

    result = latex_pdf.write_latex_pdf(
        model,
        output,
        media_asset_directory=asset_directory,
    )

    assert result == output
    assert output.read_bytes() == b"%PDF-test"
