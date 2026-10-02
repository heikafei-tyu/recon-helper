from pathlib import Path

from ..errors import ReadError
from . import csv_reader, json_reader, xlsx_reader


def read_table(filename, encoding=None, sheet_name=None, sheet_index=0):
    path = Path(filename)
    readers = {".csv": csv_reader.read, ".tsv": csv_reader.read, ".json": json_reader.read, ".xlsx": xlsx_reader.read}
    reader = readers.get(path.suffix.lower())
    if reader is None:
        raise ReadError(f"不支持的文件格式：{path.suffix}")
    if path.suffix.lower() == ".xlsx":
        return reader(path, encoding, sheet_name, sheet_index)
    return reader(path, encoding)
