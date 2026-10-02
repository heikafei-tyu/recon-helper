import pytest

from recon.filters import matches
from recon.transforms import transform


def test_filters_numeric_and_text():
    assert matches({"amount": "10", "name": "alpha"}, [{"field": "amount", "op": "gte", "value": 10}, {"field": "name", "op": "contains", "value": "ph"}])
    assert not matches({"amount": "9"}, [{"field": "amount", "op": "gt", "value": 10}])


def test_transforms():
    assert transform(" 10.00 ", ["trim", "decimal"]) == "10.00"
    assert transform(" AbC ", ["trim", "casefold"]) == "abc"
    with pytest.raises(ValueError):
        transform("x", ["decimal"])
