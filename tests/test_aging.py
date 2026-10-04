import pytest

from recon.aging import aging_structure, compare_aging

ROWS = [{"due": "2024-01-01", "amount": 100}, {"due": "2024-02-15", "amount": 50}]


def test_aging_structure_and_compare():
    current = aging_structure(ROWS, "due", as_of="2024-03-01")
    assert current["0-60"]["amount"] == "100"
    assert compare_aging(current, current)["0-60"]["change"] == "0"


@pytest.mark.parametrize("rows", [[], [{"due": "bad", "amount": 1}], [{"due": "2024-01-01", "amount": "x"}]])
def test_aging_invalid(rows):
    with pytest.raises((ValueError, KeyError)):
        aging_structure(rows, "due", as_of="2024-03-01")
