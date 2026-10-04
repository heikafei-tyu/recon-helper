import pytest

from recon.fx import FXRates


def test_fx():
    assert FXRates({"USD": 7.2}).convert(10, "USD") == 72


@pytest.mark.parametrize("source", ["EUR", "GBP", "JPY"])
def test_fx_missing(source):
    with pytest.raises(ValueError):
        FXRates({"USD": 7.2}).convert(1, source)
