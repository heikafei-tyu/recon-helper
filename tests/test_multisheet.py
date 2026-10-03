from openpyxl import Workbook
import pytest

from recon.engine import run_rules
from recon.readers import read_workbook


def make_book(path):
    book = Workbook()
    first = book.active
    first.title = "明细"
    first.append(["id", "amount"])
    first.append(["a", 100])
    second = book.create_sheet("汇总")
    second.append(["id", "amount"])
    second.append(["a", 100])
    book.save(path)


def test_read_all_sheets_and_cross_sheet_rule(tmp_path):
    source = tmp_path / "book.xlsx"
    make_book(source)
    assert set(read_workbook(source)) == {"明细", "汇总"}
    rules = tmp_path / "rules.yaml"
    rules.write_text("left: book.xlsx\nright: book.xlsx\nleft_sheet: 明细\nright_sheet: 汇总\nkey: id\ncolumns: [amount]\n", encoding="utf-8")
    assert run_rules(rules)["differences"] == []


@pytest.mark.parametrize("sheet", ["不存在", "", "明细2"])
def test_invalid_sheet_rejected(tmp_path, sheet):
    source = tmp_path / "book.xlsx"
    make_book(source)
    rules = tmp_path / "rules.yaml"
    rules.write_text(f"left: book.xlsx\nright: book.xlsx\nleft_sheet: {sheet}\nright_sheet: 汇总\nkey: id\ncolumns: [amount]\n", encoding="utf-8")
    with pytest.raises(ValueError):
        run_rules(rules)
