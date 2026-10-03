from pathlib import Path
from recon.engine import run_rules


def test_multicurrency_import_export():
    result = run_rules(Path("examples/scenarios/multicurrency_import_export/rules.yaml"))
    assert result["differences"] == []
