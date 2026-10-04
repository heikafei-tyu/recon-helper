from pathlib import Path

from recon.engine import run_rules


def test_installment_contract_scenario():
    assert run_rules(Path(__file__).parent / "installment_contract" / "rules.yaml")["differences"] == []
