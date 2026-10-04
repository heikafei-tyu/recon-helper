import pytest

from recon.model import Table
from recon.quality import assess_table


def test_clean_table_scores_full():
    table = Table(("id", "amount"), (("a", "10"), ("b", "20")))
    result = assess_table(table, ["id"], {"amount": "number"})
    assert result["score"] == 100 and result["passed"]


def test_dirty_table_contains_deduction_details():
    table = Table(("id", "amount"), (("a", None), ("a", "bad"), ("c", "3")))
    result = assess_table(table, ["id"], {"amount": "number"}, threshold=90)
    assert result["score"] < 90 and not result["passed"]
    assert set(result["deductions"]) == {"empty", "type", "duplicates", "key"}


def test_empty_table_is_valid_but_not_full_quality():
    result = assess_table(Table(("id",), ()), ["id"])
    assert result["score"] == 100 and result["rows"] == 0


@pytest.mark.parametrize("threshold", [-1, 101, "70"])
def test_invalid_threshold_rejected(threshold):
    with pytest.raises(ValueError):
        assess_table(Table(("id",), (("a",),)), threshold=threshold)


def test_missing_key_rejected():
    with pytest.raises(ValueError, match="主键"):
        assess_table(Table(("id",), (("a",),)), ["missing"])


def test_non_table_rejected():
    with pytest.raises(TypeError):
        assess_table([], ["id"])
