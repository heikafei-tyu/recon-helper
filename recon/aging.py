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


def compare_aging(current, previous):
    keys = list(dict.fromkeys([*current, *previous]))
    return {key: {"current_ratio": current.get(key, {}).get("ratio", "0"), "previous_ratio": previous.get(key, {}).get("ratio", "0"), "change": str(Decimal(current.get(key, {}).get("ratio", "0")) - Decimal(previous.get(key, {}).get("ratio", "0"))).replace("0E-28", "0")} for key in keys}
