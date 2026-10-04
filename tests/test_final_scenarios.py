from pathlib import Path

from recon.engine import run_rules


def test_final_scenarios():
    for name in ("department_expense_mom", "accounts_offset", "multisheet_consolidation", "fixed_width_payroll", "tsv_large_reconciliation"):
        assert run_rules(Path("examples/scenarios") / name / "rules.yaml")["differences"] == []
