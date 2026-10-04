import pytest

from recon.severity import classify, exit_code


@pytest.mark.parametrize(
    "status,level", [("left_only", "fatal"), ("mismatch", "serious"), ("within_tolerance", "notice")]
)
def test_grade(status, level):
    assert classify({"status": status}) == level


def test_fatal_exit():
    assert exit_code([{"status": "data_missing"}]) == 2


@pytest.mark.parametrize("rows", [[], [{"status": "within_tolerance"}], [{"status": "mismatch"}]])
def test_nonfatal_exit(rows):
    assert exit_code(rows) == 0
