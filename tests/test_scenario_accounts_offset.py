from pathlib import Path
from recon.engine import run_rules
def test_accounts_offset(): assert not run_rules(Path('examples/scenarios/accounts_offset/rules.yaml'))['differences']
