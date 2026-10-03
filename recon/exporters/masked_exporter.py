import re
from decimal import ROUND_HALF_UP, Decimal

from .common import write_parent


def mask_value(value, rule):
    if value is None:
        return None
    text = str(value)
    if rule == "name":
        return text[:1] + "*" * max(0, len(text) - 1)
    if rule == "phone":
        return text[:3] + "****" + text[-4:]
    if rule == "amount":
        return str(Decimal(text).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if rule == "email":
        return re.sub(r"(?<=.).(?=[^@]*@)", "*", text)
    raise ValueError(f"未知脱敏规则：{rule}")


def mask_rows(rows, columns):
    if not isinstance(columns, dict):
        raise ValueError("columns 必须是对象")
    return [{**row, **{column: mask_value(row.get(column), rule) for column, rule in columns.items()}} for row in rows]


def export_masked_csv(rows, columns, output):
    import csv
    path = write_parent(output)
    masked = mask_rows(rows, columns)
    fields = sorted({key for row in masked for key in row})
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(masked)
    return {"output": str(path), "rows": len(masked)}
