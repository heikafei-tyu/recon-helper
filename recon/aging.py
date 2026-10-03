from collections import OrderedDict
from datetime import date
from decimal import Decimal, InvalidOperation

BUCKETS = (30, 60, 90, 180, 360)


def aging_structure(rows, due_column="due_date", amount_column="amount", as_of=None, buckets=BUCKETS):
    if not rows:
        raise ValueError("账龄数据不能为空")
    as_of = date.fromisoformat(as_of) if as_of else date.today()
    totals = OrderedDict((f"0-{limit}", Decimal("0")) for limit in buckets)
    totals[f"{buckets[-1]}+"] = Decimal("0")
    for row in rows:
        due = date.fromisoformat(str(row[due_column]))
        age = max(0, (as_of - due).days)
        target = next((f"0-{limit}" for limit in buckets if age <= limit), f"{buckets[-1]}+")
        try:
            totals[target] += Decimal(str(row[amount_column]))
        except InvalidOperation as exc:
            raise ValueError(f"金额非法：{row[amount_column]}") from exc
    total = sum(totals.values(), Decimal("0"))
    return {key: {"amount": str(value), "ratio": str(value / total if total else 0)} for key, value in totals.items()}


def compare_aging(current, previous, threshold="0.05"):
    """Compare bucket ratios and classify material deterioration/improvement."""
    try:
        limit = Decimal(str(threshold))
    except InvalidOperation as exc:
        raise ValueError("账龄变化阈值非法") from exc
    if limit < 0:
        raise ValueError("账龄变化阈值不能为负数")
    keys = list(dict.fromkeys([*current, *previous]))
    result = {}
    for key in keys:
        now = Decimal(current.get(key, {}).get("ratio", "0")); old = Decimal(previous.get(key, {}).get("ratio", "0")); change = now - old
        label = "稳定"
        if abs(change) > limit:
            older_bucket = key.endswith("+") or key.startswith("180") or key.startswith("360")
            label = "账龄恶化" if (older_bucket and change > 0) else "账龄改善" if change < 0 else "账龄恶化"
        result[key] = {"current_ratio": str(now), "previous_ratio": str(old), "change": str(change).replace("0E-28", "0"), "threshold": str(limit), "assessment": label}
    return result
