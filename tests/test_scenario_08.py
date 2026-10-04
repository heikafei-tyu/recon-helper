from pathlib import Path

from recon.engine import run_rules


def test_commission_reconciliation():
    result = run_rules(Path("examples/scenarios/commission_reconciliation/rules.yaml"))
    assert result["differences"] == []
