"""基于 IQR 的离群值检测。"""

from decimal import Decimal


def _percentile(values, fraction):
    values = sorted(values)
    position = (len(values) - 1) * fraction
    lower, upper = int(position), min(int(position) + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * Decimal(str(position - lower))


def detect_iqr(rows, column, multiplier=Decimal("1.5")):
    values = []
    indexed = []
    for index, row in enumerate(rows):
        if row.get(column) in (None, ""):
            continue
        value = Decimal(str(row[column]).replace(",", ""))
        values.append(value)
        indexed.append((index, value))
    if len(values) < 4:
        return []
    q1, q3 = _percentile(values, Decimal("0.25")), _percentile(values, Decimal("0.75"))
    low, high = q1 - multiplier * (q3 - q1), q3 + multiplier * (q3 - q1)
    return [
        {"row": index, "value": str(value), "lower": str(low), "upper": str(high)}
        for index, value in indexed
        if value < low or value > high
    ]


def iqr_bounds(values, multiplier=Decimal("1.5")):
    numbers = sorted(Decimal(str(value)) for value in values)
    if len(numbers) < 4:
        return None
    q1, q3 = _percentile(numbers, Decimal(".25")), _percentile(numbers, Decimal(".75"))
    return q1 - multiplier * (q3 - q1), q3 + multiplier * (q3 - q1)


def anomaly_rate(rows, column):
    return len(detect_iqr(rows, column)) / len(rows) if rows else 0


def mark_anomalies(rows, column):
    indexes = {item["row"] for item in detect_iqr(rows, column)}
    return [{**dict(row), "anomaly": index in indexes} for index, row in enumerate(rows)]
