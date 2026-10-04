from pathlib import Path

from recon.engine import run_rules


def test_department_expense():
    assert not run_rules(Path("examples/scenarios/department_expense_mom/rules.yaml"))["differences"]
