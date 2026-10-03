from pathlib import Path

import pytest

from recon.engine import run_rules

SCENARIOS = ["multi_currency", "period_anomaly", "aging", "missing_month_new", "cross_sheet_new"]
@pytest.mark.parametrize("name", SCENARIOS)
def test_new_scenario(name):
    path = Path("examples/scenarios") / name / "rules.yaml"
    assert "differences" in run_rules(path)
