from pathlib import Path

from recon.quality import assess_file


def test_quality_scenario():
    root = Path(__file__).parent / "quality_demo"
    clean = assess_file(root / "clean.csv", ["id"], {"amount": "number"})
    dirty = assess_file(root / "dirty.csv", ["id"], {"amount": "number"})
    assert clean["score"] == 100 and dirty["score"] < 70
