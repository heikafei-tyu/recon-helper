from openpyxl import Workbook

from recon.benchmark import benchmark


def test_xlsx_stream_benchmark(tmp_path):
    path = tmp_path / "data.xlsx"
    book = Workbook(); sheet = book.active; sheet.append(["id", "amount"])
    for index in range(100): sheet.append([index, index * 2])
    book.save(path)
    result = benchmark(path, key="id")
    assert result["format"] == "xlsx" and result["rows"] == 100
