from datetime import date


def select_rows(rows, scope):
    if not isinstance(scope, dict):
        raise ValueError("scope 必须是对象")
    selected = list(rows)
    description = []
    if "first_n" in scope:
        if not isinstance(scope["first_n"], int) or scope["first_n"] < 0:
            raise ValueError("scope.first_n 必须是非负整数")
        selected = selected[: scope["first_n"]]
        description.append(f"前 {scope['first_n']} 行")
    if "department" in scope:
        field = scope.get("department_column", "department")
        selected = [row for row in selected if row.get(field) == scope["department"]]
        description.append(f"部门={scope['department']}")
    if "date_from" in scope or "date_to" in scope:
        field = scope.get("date_column", "date")
        start = date.fromisoformat(scope.get("date_from", "0001-01-01"))
        end = date.fromisoformat(scope.get("date_to", "9999-12-31"))
        selected = [row for row in selected if start <= date.fromisoformat(str(row[field])) <= end]
        description.append(f"日期 {start.isoformat()} 至 {end.isoformat()}")
    return selected, "；".join(description) if description else "全部数据"
