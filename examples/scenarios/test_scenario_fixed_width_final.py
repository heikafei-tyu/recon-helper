from pathlib import Path
from recon.readers.fixed_width_reader import read

def test_fixed_width_payroll_scenario():
    root = Path(__file__).parent / "fixed_width_payroll_final"
    table = read(root / "payroll.txt", [4, 6, 6, 6, 6], ["employee", "month", "gross", "tax", "net"])
    assert len(table.rows) == 3 and table.rows[0][0] == "E001"
