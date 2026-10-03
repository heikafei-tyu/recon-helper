"""表结构和质量校验。"""
from decimal import Decimal, InvalidOperation


def validate_schema(rows, required=None, types=None, max_null_rate=1):
    rows = [dict(row) for row in rows]
    required, types = required or [], types or {}
    columns = set().union(*(row.keys() for row in rows)) if rows else set()
    errors = [f"缺少列：{name}" for name in required if name not in columns]
    for column, expected in types.items():
        for index, row in enumerate(rows):
            value = row.get(column)
            if value in (None, ""):
                continue
            try:
                if expected in ("number", "decimal"):
                    Decimal(str(value).replace(",", ""))
                elif expected == "integer":
                    int(str(value))
                elif expected == "text" and not isinstance(value, str):
                    raise ValueError
            except (ValueError, InvalidOperation, TypeError):
                errors.append(f"{column} 第 {index + 1} 行类型错误")
                break
    for column in columns:
        rate = sum(row.get(column) in (None, "") for row in rows) / len(rows) if rows else 0
        if rate > max_null_rate:
            errors.append(f"{column} 空值率 {rate:.2%} 超过阈值")
    return errors
