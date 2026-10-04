from pathlib import Path

from recon.engine import run_rules


def test_fx_gain_loss_scenario():
    assert run_rules(Path(__file__).parent / "fx_gain_loss" / "rules.yaml")["differences"] == []
