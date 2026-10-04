from pathlib import Path

from recon.engine import run_rules


def test_deferred_tax_reconciliation():
    result = run_rules(Path(__file__).parent / "deferred_tax" / "rules.yaml")
    assert result["differences"] == []
