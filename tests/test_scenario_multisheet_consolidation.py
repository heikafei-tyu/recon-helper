from pathlib import Path
from recon.engine import run_rules
def test_multisheet_consolidation(): assert not run_rules(Path('examples/scenarios/multisheet_consolidation/rules.yaml'))['differences']
