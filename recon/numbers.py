import re
from decimal import Decimal, InvalidOperation


def normalize_number(value):
    """Normalize common display forms without changing the source text in reports."""
    if value is None:
        return None
    text = str(value).strip().replace(" ", "")
    if not text:
        return None
    percent = text.endswith("%")
    if percent:
        text = text[:-1]
    text = re.sub(r"^[¥￥$€£]", "", text)
    text = text.replace(",", "")
    try:
        number = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"无法识别数字：{value}") from exc
    if not number.is_finite():
        raise ValueError(f"数字必须是有限值：{value}")
    return number / 100 if percent else number
