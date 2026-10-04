import pytest

from recon.scope import select_rows

ROWS = [{"id": 1, "department": "A", "date": "2024-01-01"}, {"id": 2, "department": "B", "date": "2024-02-01"}]


def test_scope_modes():
    assert len(select_rows(ROWS, {"first_n": 1})[0]) == 1
    assert len(select_rows(ROWS, {"department": "A"})[0]) == 1
    assert len(select_rows(ROWS, {"date_from": "2024-02-01"})[0]) == 1


@pytest.mark.parametrize("scope", [{"first_n": -1}, {"first_n": "1"}, {"date_from": "bad"}])
def test_scope_invalid(scope):
    with pytest.raises((ValueError, KeyError)):
        select_rows(ROWS, scope)
