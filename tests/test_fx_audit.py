import pytest

from recon.fx import FXRates


def test_fx_quotes_fresh():
    assert FXRates.validate_quotes([{"currency": "USD", "date": "2024-01-30", "rate": "7.2"}], "2024-02-01", 30) == []


def test_fx_quote_expired():
    result = FXRates.validate_quotes([{"currency": "USD", "date": "2024-01-01", "rate": "7.2"}], "2024-02-15", 30)
    assert result[0]["status"] == "rate_expired"


def test_fx_same_day_conflict():
    result = FXRates.validate_quotes(
        [
            {"currency": "USD", "date": "2024-02-01", "rate": "7.2"},
            {"currency": "USD", "date": "2024-02-01", "rate": "7.3"},
        ],
        "2024-02-01",
    )
    assert result[0]["status"] == "rate_conflict"


def test_fx_same_rate_is_not_conflict():
    assert (
        FXRates.validate_quotes(
            [
                {"currency": "USD", "date": "2024-02-01", "rate": "7.2"},
                {"currency": "USD", "date": "2024-02-01", "rate": "7.2"},
            ],
            "2024-02-01",
        )
        == []
    )


def test_fx_invalid_quote_fields():
    with pytest.raises(ValueError):
        FXRates.validate_quotes([{"currency": "USD", "date": "bad", "rate": 7}], "2024-02-01")
    with pytest.raises(ValueError):
        FXRates.validate_quotes([{"currency": "USD", "date": "2024-02-01", "rate": 0}], "2024-02-01")
