from pathlib import Path

from ..errors import ReadError
from .options import ReaderOptions
from .stream import iter_rows

__all__ = ["ReaderOptions", "iter_rows", "read_table", "read_workbook"]


def read_table(filename, encoding=None, sheet_name=None, sheet_index=0, skip_rows=0):
    from . import (  # noqa: F401
        csv_reader,
        fixed_width_reader,
        json_reader,
        ods_reader,
        parquet_reader,
        tsv_reader,
        xls_reader,
        xlsx_reader,
        xml_reader,
    )

    path = Path(filename)
    if not path.exists():
        raise ReadError(f"输入文件不存在：{path}")
    if not path.is_file():
        raise ReadError(f"输入路径不是文件：{path}")
    readers = {
        ".csv": csv_reader.read,
        ".tsv": tsv_reader.read,
        ".json": json_reader.read,
        ".xlsx": xlsx_reader.read,
        ".xls": xls_reader.read,
        ".parquet": parquet_reader.read,
        ".ods": ods_reader.read,
        ".xml": xml_reader.read,
    }
    reader = readers.get(path.suffix.lower())
    if reader is None:
        raise ReadError(f"不支持的文件格式：{path.suffix}")
    if path.suffix.lower() == ".xlsx":
        return reader(path, encoding, sheet_name, sheet_index, skip_rows)
    if path.suffix.lower() == ".ods":
        return reader(path, encoding, sheet_name)
    return reader(path, encoding)


def read_workbook(filename):
    from . import xlsx_reader

    path = Path(filename)
    if not path.exists():
        raise ReadError(f"输入文件不存在：{path}")
    if not path.is_file():
        raise ReadError(f"输入路径不是文件：{path}")
    if path.suffix.lower() != ".xlsx":
        raise ReadError("多工作表读取只支持 XLSX")
    return xlsx_reader.read_sheets(path)
