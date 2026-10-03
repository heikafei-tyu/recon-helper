from pathlib import Path
from recon.engine import run_rules
def test_supplier(): assert run_rules(Path("examples/scenarios/supplier_reconciliation/rules.yaml"))["differences"] == []
