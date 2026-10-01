from pathlib import Path

from ..errors import ReadError
from . import csv_reader, json_reader, xlsx_reader


def read_table(filename, encoding=None):
    path = Path(filename)
    readers = {".csv": csv_reader.read, ".json": json_reader.read, ".xlsx": xlsx_reader.read}
    reader = readers.get(path.suffix.lower())
    if reader is None:
        raise ReadError(f"不支持的文件格式：{path.suffix}")
    return reader(path, encoding)
