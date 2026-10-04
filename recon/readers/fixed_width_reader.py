from ..errors import ReadError
from ..model import Table


def read(path, widths, columns=None, encoding="utf-8"):
    if not isinstance(widths, list) or not widths or any(not isinstance(item, int) or item <= 0 for item in widths):
        raise ValueError("固定宽度列宽必须是正整数列表")
    columns = columns or [f"column_{i + 1}" for i in range(len(widths))]
    if len(columns) != len(widths):
        raise ValueError("列名数量必须等于列宽数量")
    rows = []
    try:
        for line in path.read_text(encoding=encoding).splitlines():
            if not line.strip():
                continue
            start = 0
            values = []
            for width in widths:
                values.append(line[start : start + width].strip() or None)
                start += width
            rows.append(values)
    except (OSError, UnicodeError) as exc:
        raise ReadError(f"固定宽度文件读取失败：{exc}") from exc
    table = Table.from_records(columns, rows)
    return Table(table.columns, table.rows, str(path), "fixed_width", encoding, None)
