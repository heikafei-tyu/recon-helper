import pytest

from recon.fuzzy import match_column


def test_fuzzy():
    assert match_column("销售金额", ["销售额", "数量"], 3)["name"] == "销售额"


@pytest.mark.parametrize("value", ["", None, 1])
def test_fuzzy_invalid(value):
    with pytest.raises(ValueError):
        match_column(value, ["金额"])
