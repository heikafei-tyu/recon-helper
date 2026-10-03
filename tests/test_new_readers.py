from openpyxl import Workbook
import pytest

from recon.readers import read_table
from recon.readers.fixed_width_reader import read as read_fixed


def test_tsv_reader(tmp_path):
    path = tmp_path / "a.tsv"; path.write_text("id\tamount\nA1\t10\n", encoding="utf-8")
    assert read_table(path).summary()["row_count"] == 1


def test_fixed_width_reader(tmp_path):
    path = tmp_path / "a.dat"; path.write_text("A1  0010\n", encoding="utf-8")
    table = read_fixed(path, [4, 4], ["id", "amount"])
    assert table.rows == (("A1", "0010"),)


def test_fixed_width_invalid(tmp_path):
    with pytest.raises(ValueError): read_fixed(tmp_path / "x", [0])


def test_xlsx_header_offset(tmp_path):
    path = tmp_path / "a.xlsx"; book = Workbook(); sheet = book.active; sheet.append(["说明"]); sheet.append(["id", "amount"]); sheet.append(["A1", 10]); book.save(path)
    assert read_table(path, skip_rows=1).columns == ("id", "amount")
