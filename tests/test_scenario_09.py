from pathlib import Path

from recon.engine import run_rules


def test_budget_actual():
    result = run_rules(Path("examples/scenarios/budget_actual/rules.yaml"))
    assert result["differences"] == []
