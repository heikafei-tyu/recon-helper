from pathlib import Path

from recon.engine import run_rules


def test_foreign_translation_reconciliation():
    result = run_rules(Path(__file__).parent / "foreign_translation" / "rules.yaml")
    assert result["differences"] == []
