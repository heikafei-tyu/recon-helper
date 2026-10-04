from pathlib import Path

from recon.engine import run_rules


def test_bank_book_outstanding():
    result = run_rules(Path("examples/scenarios/bank_book_outstanding/rules.yaml"))
    assert len(result["differences"]) == 1
    assert result["differences"][0]["key"] == "BNK-2404"
