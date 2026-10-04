from pathlib import Path
from recon.engine import run_rules

def test_inventory_fifo_scenario():
    result = run_rules(Path(__file__).parent / "inventory_fifo" / "rules.yaml")
    assert result["differences"] == []

