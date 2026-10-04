from pathlib import Path

from recon.engine import run_rules


def test_revenue_cost_matching_reconciliation():
    result = run_rules(Path(__file__).parent / "revenue_cost_matching" / "rules.yaml")
    assert result["differences"] == []
