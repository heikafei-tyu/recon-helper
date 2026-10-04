from pathlib import Path
from recon.engine import run_rules


def test_budget_execution_reconciles():
    assert run_rules(Path("examples/scenarios/budget_execution/rules.yaml"))["differences"] == []


def test_deposit_flow_reconciles():
    assert run_rules(Path("examples/scenarios/deposit_flow/rules.yaml"))["differences"] == []
