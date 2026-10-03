import pytest

from recon.numbers import normalize_number


@pytest.mark.parametrize("value, expected", [("1,234.56", "1234.56"), ("¥100", "100"), ("12.3%", "0.123")])
def test_number_normalization(value, expected):
    assert str(normalize_number(value)) == expected


@pytest.mark.parametrize("value", ["", "abc", "Infinity"])
def test_invalid_number_normalization(value):
    if value == "":
        assert normalize_number(value) is None
    else:
        with pytest.raises(ValueError):
            normalize_number(value)
