import csv
import io

from ..errors import ReadError
from ..model import Table
from .encoding_detector import decode


def read(path, encoding=None):
    records = csv.reader(io.StringIO(decode(path.read_bytes(), encoding)), strict=True)
    try:
        header = next(records, None)
        if header is None:
            raise ReadError("CSV 文件为空")
        return Table.from_records(header, records)
    except csv.Error as exc:
        raise ReadError(f"CSV 格式错误：{exc}") from exc
