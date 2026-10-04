import json

import pytest
from openpyxl import Workbook

from examples.generate import generate
from recon.cli import main
from recon.errors import ReadError
from recon.readers import read_table


def test_formats_and_encodings_agree(tmp_path):
    generate(tmp_path)
    tables = [
        read_table(tmp_path / name)
        for name in ["orders.csv", "orders-gbk.csv", "orders-utf16.csv", "orders.json", "orders.xlsx"]
    ]
    assert all((table.columns, table.rows) == (tables[0].columns, tables[0].rows) for table in tables)
    assert tables[0].rows[0] == ("001", "示例甲", "12.50")
    assert tables[0].summary()["types"]["amount"] == "number"


@pytest.mark.parametrize("content", ["a,a\n1,2", "a,b\n1", "", ",b\n1,2"])
def test_invalid_csv(tmp_path, content):
    path = tmp_path / "bad.csv"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ReadError):
        read_table(path)


@pytest.mark.parametrize("content", ["[]", "{}", '[{"a":1},{"b":2}]', "{broken"])
def test_invalid_json(tmp_path, content):
    path = tmp_path / "bad.json"
    path.write_text(content)
    with pytest.raises(ReadError):
        read_table(path)


def test_formula_rejected(tmp_path):
    book = Workbook()
    book.active.append(["amount"])
    book.active.append(["=1+1"])
    path = tmp_path / "formula.xlsx"
    book.save(path)
    with pytest.raises(ReadError, match="公式"):
        read_table(path)


def test_cli(tmp_path, capsys):
    generate(tmp_path)
    assert main(["read", str(tmp_path / "orders.xlsx")]) == 0
    assert json.loads(capsys.readouterr().out)["row_count"] == 2
    assert main(["read", str(tmp_path / "missing.csv")]) == 2
    assert "RECON_READ_ERROR" in capsys.readouterr().err


def test_explicit_encoding(tmp_path):
    path = tmp_path / "table.csv"
    path.write_bytes("编号\n001\n".encode("utf-16-le"))
    with pytest.raises(ReadError):
        read_table(path)
    assert read_table(path, "utf-16-le").rows == (("001",),)


@pytest.mark.parametrize("target_kind", ["missing", "directory"])
def test_input_path_errors_are_read_errors(tmp_path, target_kind):
    path = tmp_path / ("missing.csv" if target_kind == "missing" else "folder.csv")
    if target_kind == "directory":
        path.mkdir()
    with pytest.raises(ReadError, match="输入文件不存在|输入路径不是文件"):
        read_table(path)


def test_empty_extension_is_reported_as_unsupported(tmp_path):
    path = tmp_path / "table"
    path.write_text("id\n1\n", encoding="utf-8")
    with pytest.raises(ReadError, match="不支持的文件格式"):
        read_table(path)
