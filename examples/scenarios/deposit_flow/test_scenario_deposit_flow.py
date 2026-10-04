from pathlib import Path

from recon.engine import run_rules


def test_deposit_flow_reconciliation():
    result = run_rules(Path(__file__).parent / "rules.yaml")
    assert result["differences"] == []
