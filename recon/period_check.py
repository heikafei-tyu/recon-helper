from decimal import Decimal, InvalidOperation


def period_check(rows, period_column, value_column, current=None, previous=None, threshold=Decimal("0.3"), periods=None):
    """Compare two periods or detect deviations from a least-squares trend."""
    try:
        values = {str(row.get(period_column)): Decimal(str(row.get(value_column))) for row in rows if row.get(period_column) is not None and row.get(value_column) not in (None, "")}
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("period_check 数值无法解析") from exc
    if periods is not None:
        if not isinstance(periods, (list, tuple)) or len(periods) < 3:
            raise ValueError("趋势核对至少需要三个连续期间")
        missing = [str(item) for item in periods if str(item) not in values]
        if missing:
            return [{"status": "data_missing", "period": missing[0]}]
        series = [values[str(item)] for item in periods]
        n = Decimal(len(series)); mean_x = (n - 1) / 2; mean_y = sum(series, Decimal("0")) / n
        denominator = sum((Decimal(i) - mean_x) ** 2 for i in range(len(series)))
        slope = sum((Decimal(i) - mean_x) * (value - mean_y) for i, value in enumerate(series)) / denominator
        intercept = mean_y - slope * mean_x
        results = []
        for index, (period, actual) in enumerate(zip(periods, series)):
            expected = intercept + slope * Decimal(index)
            deviation = abs(actual - expected) / abs(expected) if expected else (Decimal("0") if actual == 0 else Decimal("1"))
            if deviation > Decimal(str(threshold)):
                results.append({"status": "波动异常", "period": str(period), "actual": str(actual), "trend_value": str(expected), "deviation": str(deviation), "threshold": str(threshold)})
        return results
    if current is None or previous is None:
        raise ValueError("period_check 需要 current 和 previous，或 periods")
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
