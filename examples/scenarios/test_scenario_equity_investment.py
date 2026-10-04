from pathlib import Path

from recon.engine import run_rules


def test_equity_investment_reconciliation():
    result = run_rules(Path(__file__).parent / "equity_investment" / "rules.yaml")
    assert result["differences"] == []
