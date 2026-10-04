"""无外部办公软件依赖的 OpenDocument Spreadsheet 读取器。"""

from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from ..errors import ReadError
from ..model import Table

NS = {"table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0", "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}


def _cell_text(cell: ET.Element) -> str:
    return "".join(cell.itertext()).strip()


def read(path: str | Path, encoding: str | None = None, sheet_name: str | None = None) -> Table:
    try:
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("content.xml")
        root = ET.fromstring(xml)
    except (KeyError, ET.ParseError, OSError, zipfile.BadZipFile) as exc:
        raise ReadError(f"ODS 文件读取失败：{exc}") from exc
    sheets = root.findall(".//table:table", NS)
    if sheet_name:
        sheets = [sheet for sheet in sheets if sheet.get(f"{{{NS['table']}}}name") == sheet_name]
    if not sheets:
        raise ReadError(f"ODS 未找到工作表：{sheet_name or '第一个工作表'}")
    rows: list[list[str]] = []
    for row in sheets[0].findall("table:table-row", NS):
        repeat_rows = int(row.get(f"{{{NS['table']}}}number-rows-repeated", "1"))
        values: list[str] = []
        for cell in row.findall("table:table-cell", NS):
            value = _cell_text(cell)
            repeat = int(cell.get(f"{{{NS['table']}}}number-columns-repeated", "1"))
            values.extend([value] * repeat)
        for _ in range(repeat_rows):
            if values:
                rows.append(values[:])
    if not rows:
        raise ReadError("ODS 工作表没有行数据")
    width = max(map(len, rows))
    header = [(value or f"column_{i + 1}") for i, value in enumerate(rows[0] + [""] * width)][:width]
    data = [row + [""] * (width - len(row)) for row in rows[1:]]
    table = Table.from_records(header, data)
    return Table(table.columns, table.rows, str(path), "ods", encoding or "utf-8", None, sheet_name)
