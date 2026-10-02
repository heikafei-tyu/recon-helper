from pathlib import Path


def test_build_metadata_is_present():
    assert Path("pyproject.toml").exists()
    assert Path("LICENSE").exists()
