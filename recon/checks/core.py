"""金融报表专用核对规则。"""

from datetime import datetime, timedelta
from decimal import Decimal

from ..numbers import normalize_number
from ..readers import read_table


def _records(path):
    table = read_table(path)
    return [dict(zip(table.columns, row)) for row in table.rows]


def _required(rule, names):
    missing = [name for name in names if not rule.get(name)]
    if missing:
        raise ValueError(f"金融规则缺少字段：{', '.join(missing)}")


def total_check(base, rule):
    _required(rule, ("detail", "summary", "columns"))
    if (
        not isinstance(rule["columns"], list)
        or not rule["columns"]
        or not all(isinstance(c, str) and c for c in rule["columns"])
    ):
        raise ValueError("total_check.columns 必须是非空字段列表")
    detail = _records(base / rule["detail"])
    summary = _records(base / rule["summary"])
    if not summary:
        raise ValueError("total_check 汇总表为空")
    summary_row = summary[-1]
    result = []
    for column in rule["columns"]:
        if detail and column not in detail[0]:
            raise ValueError(f"total_check 明细缺少字段：{column}")
        if column not in summary_row:
            raise ValueError(f"total_check 汇总缺少字段：{column}")
        try:
            actual = sum((normalize_number(row.get(column)) or Decimal("0") for row in detail), Decimal("0"))
            expected = normalize_number(summary_row.get(column))
        except ValueError as exc:
            raise ValueError(f"total_check 数字字段 {column} 无法解析") from exc
        if expected is None or actual != expected:
            result.append(
                {
                    "status": "total_mismatch",
                    "column": column,
                    "detail_total": str(actual),
                    "summary_total": str(expected),
                    "difference": str(actual - expected) if expected is not None else None,
                }
            )
    return result


def chain_check(base, rule):
    tables = rule.get("tables")
    if not isinstance(tables, list) or len(tables) < 2 or not all(isinstance(item, str) and item for item in tables):
        raise ValueError("chain_check.tables 必须包含至少两张表")
    start_column = rule.get("start_column", "期初")
    end_column = rule.get("end_column", "期末")
    if not isinstance(start_column, str) or not isinstance(end_column, str) or not start_column or not end_column:
        raise ValueError("chain_check.start_column/end_column 必须是非空字符串")
    loaded = []
    for name in tables:
        try:
            rows = _records(base / name)
        except FileNotFoundError as exc:
            raise ValueError(f"chain_check 文件不存在：{name}") from exc
        if not rows:
            raise ValueError(f"chain_check 表为空：{name}")
        if start_column not in rows[0] or end_column not in rows[0]:
            raise ValueError(f"chain_check 表 {name} 缺少期初或期末字段")
        loaded.append(rows)
    result = []
    for index, (current, following) in enumerate(zip(loaded, loaded[1:])):
        left, right = current[-1].get(end_column), following[0].get(start_column)
        try:
            left_number, right_number = normalize_number(left), normalize_number(right)
        except ValueError as exc:
            raise ValueError(f"chain_check 数值无法解析：{tables[index]} -> {tables[index + 1]}") from exc
        if left_number is None or right_number is None:
            raise ValueError(f"chain_check 数值不能为空：{tables[index]} -> {tables[index + 1]}")
        if left_number != right_number:
            result.append(
                {
                    "status": "chain_mismatch",
                    "from": tables[index],
                    "to": tables[index + 1],
                    "end_value": str(left),
                    "start_value": str(right),
                    "difference": str(left_number - right_number),
                }
            )
    return result


def _parse_time(value, frequency):
    text = str(value).strip()
    try:
        if frequency == "month":
            return datetime.strptime(text, "%Y-%m" if len(text) == 7 else "%Y-%m-%d").date().replace(day=1)
        if frequency == "day":
            return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"missing_check 时间值非法：{value}") from exc
    raise ValueError("missing_check.frequency 必须是 month 或 day")


def _format_time(value, frequency):
    return value.strftime("%Y-%m" if frequency == "month" else "%Y-%m-%d")


def missing_check(base, rule):
    _required(rule, ("file", "time_column"))
    frequency = rule.get("frequency", "month")
    if frequency not in ("month", "day"):
        raise ValueError("missing_check.frequency 必须是 month 或 day")
    rows = _records(base / rule["file"])
    if not rows or rule["time_column"] not in rows[0]:
        raise ValueError(f"missing_check 缺少时间字段：{rule['time_column']}")
    actual = {
        _parse_time(row[rule["time_column"]], frequency)
        for row in rows
        if row.get(rule["time_column"]) not in (None, "")
    }
    if not actual:
        return []
    start = _parse_time(rule["start"], frequency) if rule.get("start") else min(actual)
    end = _parse_time(rule["end"], frequency) if rule.get("end") else max(actual)
    if start > end:
        raise ValueError("missing_check.start 不能晚于 end")
    expected = set()
    cursor = start
    while cursor <= end:
        expected.add(cursor)
        cursor = (
            (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
            if frequency == "month"
            else cursor + timedelta(days=1)
        )
    return [
        {"status": "data_missing", "time_column": rule["time_column"], "missing": _format_time(item, frequency)}
        for item in sorted(expected - actual)
    ]


def run_finance_checks(base, checks):
    if not isinstance(checks, list):
        raise ValueError("checks 必须是规则列表")
    result = []
    for rule in checks:
        if not isinstance(rule, dict):
            raise ValueError("金融检查规则必须是对象")
        kind = rule.get("type")
        if kind == "total_check":
            result.extend(total_check(base, rule))
        elif kind == "chain_check":
            result.extend(chain_check(base, rule))
        elif kind == "missing_check":
            result.extend(missing_check(base, rule))
        elif kind == "period_check":
            from ..period_check import period_check

            rows = _records(base / rule["file"])
            result.extend(
                period_check(
                    rows,
                    rule["period_column"],
                    rule["value_column"],
                    rule.get("current"),
                    rule.get("previous"),
                    rule.get("threshold", "0.3"),
                    rule.get("periods"),
                )
            )
        else:
            raise ValueError(f"未知金融检查类型：{kind}")
    return result
