import re
from decimal import Decimal, InvalidOperation


def matches(row, conditions):
    for condition in conditions:
        field = condition["field"]
        operator = condition.get("op", "eq")
        actual = row.get(field)
        expected = condition.get("value")
        if operator in ("is_null", "not_null"):
            passed = (actual in (None, "")) if operator == "is_null" else (actual not in (None, ""))
            if not passed:
                return False
            continue
        if operator in ("gt", "gte", "lt", "lte"):
            try:
                actual_value, expected_value = Decimal(actual), Decimal(str(expected))
            except (InvalidOperation, TypeError):
                raise ValueError(f"过滤字段 {field} 必须是数值")
            passed = {
                "gt": actual_value > expected_value,
                "gte": actual_value >= expected_value,
                "lt": actual_value < expected_value,
                "lte": actual_value <= expected_value,
            }[operator]
        elif operator in ("between", "not_between"):
            if not isinstance(expected, (list, tuple)) or len(expected) != 2:
                raise ValueError(f"过滤字段 {field} 的 {operator} 需要两个边界")
            try:
                actual_value = Decimal(str(actual))
                bounds = sorted(Decimal(str(item)) for item in expected)
            except (InvalidOperation, TypeError, ValueError) as exc:
                raise ValueError(f"过滤字段 {field} 必须是数值") from exc
            passed = bounds[0] <= actual_value <= bounds[1]
            if operator == "not_between":
                passed = not passed
        elif operator in ("regex", "starts_with", "ends_with"):
            text = str(actual or "")
            if operator == "regex":
                try:
                    passed = re.search(str(expected), text) is not None
                except re.error as exc:
                    raise ValueError(f"过滤字段 {field} 的正则表达式非法") from exc
            elif operator == "starts_with":
                passed = text.startswith(str(expected))
            else:
                passed = text.endswith(str(expected))
        else:
            if operator in ("in", "not_in"):
                if not isinstance(expected, (list, tuple, set)):
                    raise ValueError(f"过滤字段 {field} 的 {operator} 需要列表")
                passed = actual in expected
                if operator == "not_in":
                    passed = not passed
            else:
                passed = {"eq": actual == expected, "ne": actual != expected, "contains": str(expected) in str(actual)}.get(operator)
                if passed is None:
                    raise ValueError(f"不支持的过滤操作：{operator}")
        if not passed:
            return False
    return True
