import pytest

from recon.errors import ReadError
from recon.model import Table
from recon.readers import read_table


def test_headers_are_trimmed_by_default(tmp_path):
    path = tmp_path / "headers.csv"
    path.write_text(" id , amount \nA1,10\n", encoding="utf-8")
    assert read_table(path).columns == ("id", "amount")


@pytest.mark.parametrize("header,expected", [(["id", "id"], "列名不能重复"), (["", "amount"], "列名不能为空")])
def test_header_errors_include_diagnostic_context(header, expected):
    with pytest.raises(ReadError, match=expected):
        Table.from_records(header, [["A", "1"]])


def test_header_duplicate_error_includes_columns():
    with pytest.raises(ReadError, match="第1,2列"):
        Table.from_records(["id", "id"], [["A", "1"]])


def test_empty_header_error_includes_column_number():
    with pytest.raises(ReadError, match="第 1 列"):
        Table.from_records([None, "amount"], [["A", "1"]])
