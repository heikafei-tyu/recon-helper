import csv

from ..errors import ReadError
from ..model import Table
from .encoding_detector import decode


def read(path, encoding=None):
    try:
        records = csv.reader(decode(path.read_bytes(), encoding).splitlines(), delimiter="\t")
        header = next(records, None)
        if header is None:
            raise ReadError("TSV 文件为空")
        table = Table.from_records(header, records)
        return Table(table.columns, table.rows, str(path), "tsv", encoding or "auto", "\t")
    except csv.Error as exc:
        raise ReadError(f"TSV 格式错误：{exc}") from exc
