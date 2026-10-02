from datetime import date
from decimal import Decimal, InvalidOperation


def infer(values):
    values = [value for value in values if value is not None and value != ""]
    if not values:
        return "empty"
    lowered = {str(value).strip().casefold() for value in values}
    if lowered <= {"true", "false"}:
        return "boolean"
    numeric = []
    for value in values:
        try:
            numeric.append(Decimal(str(value)))
        except (InvalidOperation, ValueError):
            numeric = []
            break
    if numeric:
        return "integer" if all(value == value.to_integral_value() for value in numeric) else "number"
    dates = []
    for value in values:
        try:
            dates.append(date.fromisoformat(str(value).strip()))
        except ValueError:
            dates = []
            break
    if dates:
        return "date"
    return "text"
