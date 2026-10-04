import json

from ..errors import ReadError
from ..model import Table
from .encoding_detector import decode


def read(path, encoding=None):
    try:
        records = json.loads(decode(path.read_bytes(), encoding))
    except json.JSONDecodeError as exc:
        raise ReadError(f"JSON 格式错误：{exc}") from exc
    if not isinstance(records, list) or not records or not all(isinstance(r, dict) for r in records):
        raise ReadError("JSON 必须是非空对象数组")
    columns = list(records[0])
    if any(set(record) != set(columns) for record in records):
        raise ReadError("JSON 每行字段必须一致")
    table = Table.from_records(columns, ([record[c] for c in columns] for record in records))
    return Table(table.columns, table.rows, str(path), "json", encoding or "auto")
