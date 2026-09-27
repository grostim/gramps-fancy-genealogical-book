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
    assert "GrampsFancyBook/GrampsFancyBook.gpr.py" in names
    assert "GrampsFancyBook/gramps_fancy_book/export.py" in names
    assert all(name.endswith((".py", "/MANIFEST")) for name in names)
    assert not any("__pycache__" in name or ".work" in name for name in names)
