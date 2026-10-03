import pytest
from recon.multicurrency import convert, validate_rates
def test_currency_date(): assert convert(10, "USD", "CNY", {"USD/CNY": {"rate": 7.2, "date": "2024-01-01"}}, "2024-01-10") == 72
@pytest.mark.parametrize("rates", [{}, {"USD/CNY": 0}, {"BAD": 1}])
def test_currency_invalid(rates):
    with pytest.raises(ValueError): validate_rates(rates)
@pytest.mark.parametrize("day", ["2024-03-01", "2025-01-01", "2023-01-01"])
def test_currency_expired(day):
    with pytest.raises(ValueError): convert(1, "USD", "CNY", {"USD/CNY": {"rate": 7, "date": "2024-01-01"}}, day, 30)
