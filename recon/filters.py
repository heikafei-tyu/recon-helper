from decimal import Decimal, InvalidOperation


def matches(row, conditions):
    for condition in conditions:
        field = condition["field"]
        operator = condition.get("op", "eq")
        actual = row.get(field)
        expected = condition.get("value")
        if operator in ("gt", "gte", "lt", "lte"):
            try:
                actual_value, expected_value = Decimal(actual), Decimal(str(expected))
            except (InvalidOperation, TypeError):
                raise ValueError(f"过滤字段 {field} 必须是数值")
            passed = {"gt": actual_value > expected_value, "gte": actual_value >= expected_value, "lt": actual_value < expected_value, "lte": actual_value <= expected_value}[operator]
        else:
            passed = {"eq": actual == expected, "ne": actual != expected, "in": actual in expected, "contains": str(expected) in str(actual)}.get(operator)
            if passed is None:
                raise ValueError(f"不支持的过滤操作：{operator}")
        if not passed:
            return False
    return True
