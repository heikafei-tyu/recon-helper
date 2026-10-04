"""列画像统计。"""

from decimal import Decimal, InvalidOperation


def column_profile(rows):
    rows = [dict(row) for row in rows]
    columns = sorted({key for row in rows for key in row})
    output = {}
    for column in columns:
        values = [row.get(column) for row in rows]
        nonempty = [value for value in values if value not in (None, "")]
        numbers = []
        for value in nonempty:
            try:
                numbers.append(Decimal(str(value).replace(",", "")))
            except (InvalidOperation, ValueError):
                pass
        kinds = "number" if numbers == [*numbers] and len(numbers) == len(nonempty) and nonempty else "text"
        output[column] = {
            "type": kinds,
            "null_count": len(values) - len(nonempty),
            "unique_count": len(set(map(str, nonempty))),
            "mean": str(sum(numbers) / len(numbers)) if numbers else None,
            "min": str(min(numbers)) if numbers else (min(map(str, nonempty)) if nonempty else None),
            "max": str(max(numbers)) if numbers else (max(map(str, nonempty)) if nonempty else None),
        }
    return output


def profile_column(rows, column):
    return column_profile([{column: row.get(column)} for row in rows]).get(column, {})


def numeric_columns(profile):
    return [name for name, data in profile.items() if data.get("type") == "number"]


def null_rates(profile, row_count):
    if row_count < 0:
        raise ValueError("row_count 不能为负")
    return {name: data["null_count"] / row_count if row_count else 0 for name, data in profile.items()}
