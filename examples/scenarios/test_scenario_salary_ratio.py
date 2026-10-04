from pathlib import Path

from recon.engine import run_rules


def test_salary_ratio_scenario():
    result = run_rules(Path(__file__).parent / "salary_ratio" / "rules.yaml")
    assert len(result["differences"]) == 1 and result["differences"][0]["key"] == ["E002", "2024-10"]
