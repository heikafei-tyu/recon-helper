from pathlib import Path
from recon.engine import run_rules


def test_consolidated_elimination_advanced_reconciliation():
    result = run_rules(Path(__file__).parent / "consolidated_elimination_advanced" / "rules.yaml")
    assert result["differences"] == []
