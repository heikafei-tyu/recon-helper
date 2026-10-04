from pathlib import Path

from recon.engine import run_rules


def test_tax_calculation_scenario():
    assert run_rules(Path(__file__).parent / "tax_calculation" / "rules.yaml")["differences"] == []
