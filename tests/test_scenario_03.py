from pathlib import Path
from recon.engine import run_rules
def test_inventory(): assert run_rules(Path("examples/scenarios/inventory_balance/rules.yaml"))["differences"] == []
