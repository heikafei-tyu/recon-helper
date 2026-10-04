from pathlib import Path
from recon.engine import run_rules

def test_project_cost_scenario():
    assert run_rules(Path(__file__).parent / "project_cost" / "rules.yaml")["differences"] == []
