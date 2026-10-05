import importlib.util
import tarfile
from pathlib import Path


def test_archive_is_reproducible_and_contains_only_runtime_files(tmp_path):
    path = Path(__file__).resolve().parents[1] / "build_addon.py"
    spec = importlib.util.spec_from_file_location("build_addon", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    first = module.build_addon(tmp_path / "first.tgz")
    second = module.build_addon(tmp_path / "second.tgz")
    assert first.read_bytes() == second.read_bytes()
    with tarfile.open(first) as archive:
        names = archive.getnames()
        license_member = archive.extractfile("GrampsFancyBook/LICENSE")
        assert license_member is not None
        license_bytes = license_member.read()
        manifest_member = archive.extractfile("GrampsFancyBook/MANIFEST")
        assert manifest_member is not None
        manifest_lines = manifest_member.read().decode("utf-8").splitlines()
        catalog_member = archive.extractfile(
            "GrampsFancyBook/locale/fr/LC_MESSAGES/addon.mo"
        )
        assert catalog_member is not None
        catalog_magic = catalog_member.read(4)
    assert "GrampsFancyBook/GrampsFancyBook.gpr.py" in names
    assert "GrampsFancyBook/gramps_fancy_book/export.py" in names
    assert "GrampsFancyBook/gramps_fancy_book/date_ranges.py" in names
    license_name = "GrampsFancyBook/LICENSE"
    assert license_name in names
    assert license_bytes == (Path(__file__).resolve().parents[1] / "LICENSE").read_bytes()
    assert "LICENSE" in manifest_lines
    catalog = "GrampsFancyBook/locale/fr/LC_MESSAGES/addon.mo"
    assert catalog in names
    assert all(
        name.endswith((".py", "/MANIFEST")) or name in {catalog, license_name}
        for name in names
    )
    assert catalog_magic in {b"\xde\x12\x04\x95", b"\x95\x04\x12\xde"}
    assert not any("__pycache__" in name or ".work" in name for name in names)
