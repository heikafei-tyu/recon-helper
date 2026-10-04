"""Input-table data quality scoring."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import Table
from .model import Table


def _is_number(value):
    try:
        Decimal(str(value))
        return True
    except (InvalidOperation, ValueError):
        return False


def assess_table(table: Table, key_columns=None, expected_types=None, threshold=70):
    """Return a 0-100 quality score and four weighted dimension details."""
    if not isinstance(table, Table):
        raise TypeError("table 必须是 Table")
    if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 100:
        raise ValueError("threshold 必须在 0 到 100 之间")
    key_columns = list(key_columns or table.columns[:1])
    missing_keys = [column for column in key_columns if column not in table.columns]
    if missing_keys:
        raise ValueError(f"主键列不存在：{', '.join(missing_keys)}")
    rows, total_cells = list(table.rows), len(table.rows) * len(table.columns)
    empty = sum(value is None for row in rows for value in row)
    null_rate = empty / total_cells if total_cells else 0.0
    type_errors = 0
    type_detail = {}
    for index, column in enumerate(table.columns):
        values = [row[index] for row in rows if row[index] is not None]
        if not values:
            continue
        expected = (expected_types or {}).get(column)
        if expected in ("number", "integer"):
            bad = sum(not _is_number(value) for value in values)
        elif expected == "date":
            bad = sum(_parse_date(value) is None for value in values)
        elif expected == "text":
            bad = 0
        else:
            bad = 0
        type_errors += bad
        if bad:
            type_detail[column] = {"expected": expected, "errors": bad}
    type_error_rate = type_errors / total_cells if total_cells else 0.0
    duplicates = len(rows) - len({tuple(row) for row in rows}) if rows else 0
    duplicate_rate = duplicates / len(rows) if rows else 0.0
    key_values = [tuple(row[table.columns.index(column)] for column in key_columns) for row in rows]
    unique_keys = len(set(key_values))
    key_error_rate = 1 - unique_keys / len(key_values) if key_values else 0.0
    dimensions = {
        "null_rate": round(null_rate, 6),
        "type_error_rate": round(type_error_rate, 6),
        "duplicate_rate": round(duplicate_rate, 6),
        "key_uniqueness_rate": round(1 - key_error_rate, 6),
    }
    deductions = {
        "empty": round(null_rate * 25, 2),
        "type": round(type_error_rate * 25, 2),
        "duplicates": round(duplicate_rate * 25, 2),
        "key": round(key_error_rate * 25, 2),
    }
    score = round(max(0, 100 - sum(deductions.values())), 2)
    return {
        "source": table.source,
        "rows": len(rows),
        "score": score,
        "threshold": threshold,
        "passed": score >= threshold,
        "dimensions": dimensions,
        "deductions": deductions,
        "type_errors": type_detail,
    }


def _parse_date(value):
    from datetime import date

    try:
        return date.fromisoformat(str(value).replace("/", "-"))
    except ValueError:
        return None


def assess_file(path, key_columns=None, expected_types=None, threshold=70):
    from .readers import read_table

    return assess_table(read_table(Path(path)), key_columns, expected_types, threshold)
