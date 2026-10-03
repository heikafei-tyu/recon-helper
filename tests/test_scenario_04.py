from pathlib import Path
from recon.engine import run_rules
def test_expense_bank(): assert run_rules(Path("examples/scenarios/expense_bank/rules.yaml"))["differences"] == []
