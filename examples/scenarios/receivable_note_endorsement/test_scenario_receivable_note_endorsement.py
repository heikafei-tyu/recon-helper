from pathlib import Path

from recon.engine import run_rules


def test_receivable_note_endorsement_reconciliation():
    result = run_rules(Path(__file__).parent / "rules.yaml")
    assert result["differences"] == []
