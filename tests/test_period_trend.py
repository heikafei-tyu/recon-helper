import pytest

from recon.period_check import period_check


ROWS = [{"month": f"2024-{i:02d}", "amount": value} for i, value in enumerate((100, 110, 120, 130), 1)]


def test_trend_is_stable():
    assert period_check(ROWS, "month", "amount", threshold="0.1", periods=["2024-01", "2024-02", "2024-03", "2024-04"]) == []


def test_trend_boundary_at_threshold():
    rows = ROWS[:2] + [{"month": "2024-03", "amount": 160}, ROWS[3]]
    assert period_check(rows, "month", "amount", threshold="0.01", periods=["2024-01", "2024-02", "2024-03", "2024-04"])


def test_trend_missing_period():
    result = period_check(ROWS[:2], "month", "amount", threshold="0.1", periods=["2024-01", "2024-02", "2024-03"])
    assert result[0]["status"] == "data_missing"


def test_trend_requires_three_periods():
    with pytest.raises(ValueError):
        period_check(ROWS, "month", "amount", periods=["2024-01", "2024-02"])


def test_trend_rejects_invalid_number():
    with pytest.raises(ValueError):
        period_check([{"month": "2024-01", "amount": "bad"}], "month", "amount", periods=["2024-01", "2024-02", "2024-03"])
