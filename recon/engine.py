"""按 YAML 指定的唯一键和字段比较两张表。"""
from decimal import Decimal, InvalidOperation
from pathlib import Path

import yaml

from .readers import read_table


def run_rules(filename):
    path = Path(filename)
    try:
        config = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML 格式错误：{exc}") from exc
    if not isinstance(config, dict):
        raise ValueError("规则必须是对象")
    for field in ("left", "right", "key", "columns"):
        if field not in config:
            raise ValueError(f"规则缺少 {field}")
    if not all(isinstance(config[f], str) and config[f] for f in ("left", "right", "key")):
        raise ValueError("left/right/key 必须是非空字符串")
    columns = config["columns"]
    if not isinstance(columns, list) or not columns or not all(isinstance(c, str) for c in columns):
        raise ValueError("columns 必须是非空字段列表")
    if len(set(columns)) != len(columns):
        raise ValueError("比较字段不能重复")
    tables = [read_table(path.parent / config[side]) for side in ("left", "right")]
    indexes = []
    for table in tables:
        for column in [config["key"], *columns]:
            if column not in table.columns:
                raise ValueError(f"输入缺少字段 {column}")
        key_index = table.columns.index(config["key"])
        index = {}
        for number, row in enumerate(table.rows, 2):
            key = row[key_index]
            if key is None or not key.strip() or key in index:
                raise ValueError(f"第 {number} 行关联键为空或重复")
            index[key] = (number, dict(zip(table.columns, row)))
        indexes.append(index)
    left, right = indexes
    differences = []
    for key in sorted(left.keys() | right.keys()):
        if key not in left or key not in right:
            differences.append({"key": key, "status": "left_only" if key in left else "right_only", "left_row": left[key][0] if key in left else None, "right_row": right[key][0] if key in right else None})
            continue
        for column in columns:
            a, b = left[key][1][column], right[key][1][column]
            if a == b:
                continue
            delta = None
            try:
                da, db = Decimal(a), Decimal(b)
                if da.is_finite() and db.is_finite():
                    if da == db:
                        continue
                    delta = str(da - db)
            except (InvalidOperation, TypeError):
                pass
            differences.append({"key": key, "status": "mismatch", "left_table": config["left"], "right_table": config["right"], "left_row": left[key][0], "right_row": right[key][0], "column": column, "left_value": a, "right_value": b, "difference": delta})
    return {"left_rows": len(left), "right_rows": len(right), "differences": differences}
