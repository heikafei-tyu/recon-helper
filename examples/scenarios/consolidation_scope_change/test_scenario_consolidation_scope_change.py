from pathlib import Path
from recon.engine import run_rules


def test_consolidation_scope_change_reconciliation():
    result = run_rules(Path(__file__).parent / "rules.yaml")
    assert result["differences"] == []
