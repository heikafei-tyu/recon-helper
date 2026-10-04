from pathlib import Path

from recon.rules_diff import diff_rules


def test_rules_diff_scenario():
    root = Path(__file__).parent / "rules_diff_demo"
    result = diff_rules(root / "old.yaml", root / "new.yaml")
    paths = {item["path"] for item in result["changed"]}
    assert "key" in paths and "tolerance.amount.absolute" in paths
    assert any(item["path"] == "columns[1]" for item in result["added"])
