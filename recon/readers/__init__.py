from pathlib import Path

from ..errors import ReadError
from . import csv_reader, fixed_width_reader, json_reader, tsv_reader, xlsx_reader


def read_table(filename, encoding=None, sheet_name=None, sheet_index=0, skip_rows=0):
    path = Path(filename)
    readers = {".csv": csv_reader.read, ".tsv": tsv_reader.read, ".json": json_reader.read, ".xlsx": xlsx_reader.read}
    reader = readers.get(path.suffix.lower())
    if reader is None:
        raise ReadError(f"不支持的文件格式：{path.suffix}")
    if path.suffix.lower() == ".xlsx":
        return reader(path, encoding, sheet_name, sheet_index, skip_rows)
    return reader(path, encoding)


def read_workbook(filename):
    path = Path(filename)
    if path.suffix.lower() != ".xlsx":
        raise ReadError("多工作表读取只支持 XLSX")
    return xlsx_reader.read_sheets(path)
