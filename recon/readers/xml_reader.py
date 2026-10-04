"""读取常见的行列式 XML 表格。"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from ..errors import ReadError
from ..model import Table


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def read(path: str | Path, encoding: str | None = None) -> Table:
    """读取 ``row/cell`` XML；首行作为列名，空单元格保留为空字符串。"""
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise ReadError(f"XML 文件读取失败：{exc}") from exc
    rows: list[list[str]] = []
    for element in root.iter():
        if _local(element.tag) not in {"row", "record", "item"}:
            continue
        cells = [cell for cell in element if _local(cell.tag) in {"cell", "column", "field"}]
        if not cells:
            cells = list(element)
        values = []
        for cell in cells:
            text = "".join(cell.itertext()).strip()
            values.append(text)
        if values:
            rows.append(values)
    if not rows:
        raise ReadError("XML 文件没有找到行数据")
    width = max(len(row) for row in rows)
    header = [value or f"column_{index + 1}" for index, value in enumerate(rows[0] + [""] * width)]
    header = header[:width]
    normalized = [row + [""] * (width - len(row)) for row in rows[1:]]
    table = Table.from_records(header, normalized)
    return Table(table.columns, table.rows, str(path), "xml", encoding or "utf-8")
