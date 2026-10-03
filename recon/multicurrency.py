from datetime import date
from decimal import Decimal


def convert(value, source, target, rates, as_of=None, max_age_days=30):
    if source == target:
        return Decimal(str(value))
    key = f"{source}/{target}"
    item = rates.get(key)
    if item is None:
        raise ValueError(f"汇率缺失：{key}")
    if isinstance(item, dict):
        rate, quote_date = item.get("rate"), item.get("date")
    else:
        rate, quote_date = item, None
    if quote_date and as_of:
        age = (date.fromisoformat(as_of) - date.fromisoformat(quote_date)).days
        if age < 0 or age > max_age_days:
            raise ValueError(f"汇率过期：{key} ({quote_date})")
    return Decimal(str(value)) * Decimal(str(rate))


def validate_rates(rates, as_of=None, max_age_days=30):
    if not isinstance(rates, dict):
        raise ValueError("rates 必须是对象")
    if not rates:
        raise ValueError("rates 不能为空")
    for key, item in rates.items():
        if not isinstance(key, str) or "/" not in key:
            raise ValueError(f"汇率键非法：{key}")
        value = item.get("rate") if isinstance(item, dict) else item
        if Decimal(str(value)) <= 0:
            raise ValueError(f"汇率必须为正数：{key}")
        if isinstance(item, dict) and item.get("date") and as_of:
            convert(1, key.split("/")[0], key.split("/")[1], rates, as_of, max_age_days)
    return True
