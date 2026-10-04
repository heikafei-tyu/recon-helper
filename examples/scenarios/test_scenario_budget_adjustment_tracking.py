from pathlib import Path

from recon.engine import run_rules


def test_budget_adjustment_tracking_reconciliation():
    result = run_rules(Path(__file__).parent / "budget_adjustment_tracking" / "rules.yaml")
    assert result["differences"] == []
