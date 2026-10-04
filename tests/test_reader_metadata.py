from openpyxl import Workbook

from recon.readers import read_table


def test_delimiter_and_metadata(tmp_path):
    path = tmp_path / "table.tsv"
    path.write_text("id\tamount\n001\t2\n", encoding="utf-8")
    table = read_table(path)
    assert table.delimiter == "\t"
    assert table.format == "tsv"
    assert table.rows[0][0] == "001"


def test_xlsx_sheet_selection(tmp_path):
    book = Workbook()
    book.active.title = "Summary"
    book.active.append(["wrong"])
    detail = book.create_sheet("Details")
    detail.append(["id"])
    detail.append(["001"])
    path = tmp_path / "multi.xlsx"
    book.save(path)
    table = read_table(path, sheet_name="Details")
    assert table.sheet_name == "Details"
    assert table.rows == (("001",),)


def test_json_reader_preserves_metadata(tmp_path):
    path = tmp_path / "table.json"
    path.write_text('[{"id": "A1", "amount": 2}]', encoding="utf-8")
    table = read_table(path)
    assert table.format == "json"
    assert table.source == str(path)
