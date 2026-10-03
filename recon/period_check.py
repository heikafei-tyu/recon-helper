from decimal import Decimal


def period_check(rows, period_column, value_column, current, previous, threshold=Decimal("0.3")):
    values = {str(row.get(period_column)): Decimal(str(row.get(value_column))) for row in rows if row.get(period_column) is not None and row.get(value_column) not in (None, "")}
    if current not in values or previous not in values:
        return [{"status": "data_missing", "period": current if current not in values else previous}]
    base = values[previous]
    if base == 0:
        changed = values[current] != 0
        ratio = None
    else:
        ratio = (values[current] - base) / abs(base)
        changed = abs(ratio) > Decimal(str(threshold))
    return [{"status": "波动异常", "period": current, "previous": previous, "change_ratio": str(ratio), "threshold": str(threshold)}] if changed else []
