from pathlib import Path

from recon.engine import run_rules


def test_tiered_tolerance_scenario():
    result = run_rules(Path(__file__).parent / "tiered_tolerance_demo" / "rules.yaml")
    assert [item["tolerance_band"] for item in result["differences"]] == ["under-10k", "under-100k", "over-100k"]
