import pytest

from recon.period_check import period_check

ROWS = [{"month": "2024-01", "amount": 100}, {"month": "2024-02", "amount": 140}]
def test_period_normal_and_anomaly():
    assert period_check(ROWS, "month", "amount", "2024-02", "2024-01", ".3")
    assert period_check(ROWS, "month", "amount", "2024-02", "2024-01", ".5") == []
@pytest.mark.parametrize("current,previous", [("x", "2024-01"), ("2024-02", "x"), ("", "")])
def test_period_missing(current, previous): assert period_check(ROWS, "month", "amount", current, previous)
