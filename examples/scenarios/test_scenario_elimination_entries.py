from pathlib import Path

from recon.engine import run_rules


def test_elimination_entries_reconciliation():
    result = run_rules(Path(__file__).parent / "elimination_entries" / "rules.yaml")
    assert result["differences"] == []
