import pytest

from recon.filters import matches
from recon.transforms import transform


def test_filters_numeric_and_text():
    assert matches(
        {"amount": "10", "name": "alpha"},
        [{"field": "amount", "op": "gte", "value": 10}, {"field": "name", "op": "contains", "value": "ph"}],
    )
    assert not matches({"amount": "9"}, [{"field": "amount", "op": "gt", "value": 10}])


def test_transforms():
    assert transform(" 10.00 ", ["trim", "decimal"]) == "10.00"
    assert transform(" AbC ", ["trim", "casefold"]) == "abc"
    with pytest.raises(ValueError):
        transform("x", ["decimal"])


def test_filter_range_and_text_operations():
    assert matches({"amount": "10"}, [{"field": "amount", "op": "between", "value": [10, 20]}])
    assert matches({"name": "alpha"}, [{"field": "name", "op": "starts_with", "value": "al"}])
    assert matches({"name": "alpha"}, [{"field": "name", "op": "regex", "value": "ph"}])
    assert matches({"name": None}, [{"field": "name", "op": "is_null"}])


def test_filter_invalid_operands():
    with pytest.raises(ValueError, match="需要列表"):
        matches({"id": "a"}, [{"field": "id", "op": "in", "value": "abc"}])
    with pytest.raises(ValueError, match="正则表达式非法"):
        matches({"id": "a"}, [{"field": "id", "op": "regex", "value": "["}])


def test_transforms_finance_and_date():
    assert transform("¥1,200.00", ["currency", "decimal"]) == "1200.00"
    assert transform("12.5%", ["percent"]) == "0.125"
    assert transform("2024/01/02", ["date:%Y/%m/%d"]) == "2024-01-02"


def test_transform_date_error_is_actionable():
    with pytest.raises(ValueError, match="无法按"):
        transform("bad", ["date:%Y-%m-%d"])
