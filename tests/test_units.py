import pytest

from recon.units import convert_amount, normalize_date


@pytest.mark.parametrize(
    "value,unit,target,expected", [(1, "万元", "元", "10000"), (2, "亿", "万元", "20000"), (7.2, "USD", "元", "51.84")]
)
def test_amount_conversion(value, unit, target, expected):
    rates = {"USD": "7.2"} if unit == "USD" else None
    assert str(convert_amount(value, unit, target, rates)) == expected


@pytest.mark.parametrize("value", ["2024-01-01", "2024/1/1", "20240101"])
def test_date_formats(value):
    assert normalize_date(value) == "2024-01-01"


@pytest.mark.parametrize("value", ["bad", "", "2024-13-01"])
def test_invalid_dates(value):
    with pytest.raises(ValueError):
        normalize_date(value)


@pytest.mark.parametrize("unit,target", [("日元", "元"), ("元", "BTC"), ("USD", "USD")])
def test_invalid_units(unit, target):
    with pytest.raises(ValueError):
        convert_amount("1", unit, target, {"USD": "0"})
