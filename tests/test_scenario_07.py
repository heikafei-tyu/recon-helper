from pathlib import Path
from recon.engine import run_rules


def test_consolidated_elimination():
    result = run_rules(Path("examples/scenarios/consolidated_elimination/rules.yaml"))
    assert result["differences"] == []
