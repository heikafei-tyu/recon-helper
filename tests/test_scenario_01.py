from pathlib import Path
from recon.engine import run_rules
def test_ar_aging(): assert run_rules(Path("examples/scenarios/ar_aging_check/rules.yaml"))["differences"] == []
