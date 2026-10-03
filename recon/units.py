"""金额单位和日期口径归一化。"""
from datetime import datetime
from decimal import Decimal

UNITS = {"元": Decimal("1"), "万元": Decimal("10000"), "万": Decimal("10000"), "亿元": Decimal("100000000"), "亿": Decimal("100000000"), "USD": Decimal("1")}


def convert_amount(value, unit="元", target="元", rates=None):
    if unit not in UNITS or target not in UNITS:
        raise ValueError(f"不支持的货币单位：{unit} -> {target}")
    number = Decimal(str(value).replace(",", ""))
    rates = rates or {}
    if unit == "USD" or target == "USD":
        rate = Decimal(str(rates.get("USD", "1")))
        if rate <= 0:
            raise ValueError("USD 汇率必须为正数")
        number = number * rate if unit == "USD" else number / rate
    else:
        number = number * UNITS[unit] / UNITS[target]
    return number


def normalize_date(value):
    text = str(value).strip()
    for pattern in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"无法识别日期：{value}")


def date_period(value, period):
    normalized = normalize_date(value)
    if period == "期初":
        return normalized
    if period == "期末":
        return normalized
    raise ValueError("日期口径必须是期初或期末")
