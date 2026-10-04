from pathlib import Path

from recon.engine import run_rules


def test_tsv_large():
    assert not run_rules(Path("examples/scenarios/tsv_large_reconciliation/rules.yaml"))["differences"]
