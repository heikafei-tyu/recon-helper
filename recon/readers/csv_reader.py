import csv
import io
import csv

from ..errors import ReadError
from ..model import Table
from .encoding_detector import decode


def read(path, encoding=None):
    text = decode(path.read_bytes(), encoding)
    try:
        dialect = csv.Sniffer().sniff(text[:8192], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    records = csv.reader(io.StringIO(text), dialect, strict=True)
    try:
        header = next(records, None)
        if header is None:
            raise ReadError("CSV 文件为空")
        table = Table.from_records(header, records)
        return Table(table.columns, table.rows, str(path), "csv", encoding or "auto", dialect.delimiter)
    except csv.Error as exc:
        raise ReadError(f"CSV 格式错误：{exc}") from exc
