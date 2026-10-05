import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def infer(values):
    values = [value for value in values if value is not None and value != ""]
    if not values:
        return "empty"
    lowered = {str(value).strip().casefold() for value in values}
    if lowered <= {"true", "false"}:
        return "boolean"
    if all(_parse_date(value) is not None for value in values):
        return "date"
    numeric_values = [_parse_number(value) for value in values]
    if all(value is not None for value in numeric_values):
        return "number" if any(not value.is_integer() for value in numeric_values) else "integer"
    numeric = []
    for value in values:
        try:
            numeric.append(Decimal(str(value)))
        except (InvalidOperation, ValueError):
            numeric = []
            break
    if numeric:
        return "integer" if all(value == value.to_integral_value() for value in numeric) else "number"
    return "text"


def _parse_date(value):
    text = str(value).strip()
    for candidate in (text, text.replace("/", "-")):
        try:
            return datetime.fromisoformat(candidate).date()
        except ValueError:
            pass
    match = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", text.replace("/", "-"))
    if match:
        try:
            return date(*(int(part) for part in match.groups()))
        except ValueError:
            return None
    if len(text) == 8 and text.isdigit():
        try:
            return date(int(text[:4]), int(text[4:6]), int(text[6:]))
        except ValueError:
            return None
    return None


def _parse_number(value):
    text = str(value).strip().replace("￥", "").replace("¥", "").replace("$", "")
    if text.endswith("%"):
        text = text[:-1].strip()
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]
    text = text.replace(",", "").replace(" ", "")
    if not text or not re.fullmatch(r"[-+]?\d+(?:\.\d+)?", text):
        return None
    try:
        return float(text)
    except ValueError:
        return None
