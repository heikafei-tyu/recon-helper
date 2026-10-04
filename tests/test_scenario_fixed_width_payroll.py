from pathlib import Path

from recon.engine import run_rules


def test_fixed_width_payroll():
    assert not run_rules(Path("examples/scenarios/fixed_width_payroll/rules.yaml"))["differences"]
