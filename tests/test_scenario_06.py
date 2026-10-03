from pathlib import Path
from recon.engine import run_rules


def test_cross_year_rollforward():
    result = run_rules(Path("examples/scenarios/cross_year_rollforward/rules.yaml"))
    assert result["differences"] == []
