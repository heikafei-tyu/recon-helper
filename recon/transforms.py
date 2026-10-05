from datetime import datetime
from decimal import Decimal, InvalidOperation


def transform(value, operations):
    if value is None:
        return None
    result = str(value)
    for operation in operations:
        if operation == "trim":
            result = result.strip()
        elif operation == "casefold":
            result = result.casefold()
        elif operation == "decimal":
            try:
                number = Decimal(result)
            except InvalidOperation as exc:
                raise ValueError(f"无法转换为数字：{result}") from exc
            if not number.is_finite():
                raise ValueError(f"数字必须为有限值：{result}")
            result = str(number)
        elif operation == "percent":
            result = str(Decimal(result[:-1].strip() if result.endswith("%") else result) / Decimal("100"))
        elif operation == "currency":
            result = result.replace(",", "").replace("¥", "").replace("￥", "").replace("$", "").strip()
        elif operation.startswith("date:"):
            pattern = operation.split(":", 1)[1]
            try:
                result = datetime.strptime(result, pattern).date().isoformat()
            except (ValueError, TypeError) as exc:
                raise ValueError(f"无法按 {pattern} 转换日期：{result}") from exc
        else:
            raise ValueError(f"未知字段转换：{operation}")
    return result
