"""按 YAML 指定的唯一键和字段比较两张表。"""
from decimal import Decimal, InvalidOperation
from decimal import ROUND_HALF_UP
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
    tolerance = config.get("tolerance", {})
    if tolerance is None:
        tolerance = {}
    if not isinstance(tolerance, dict):
        raise ValueError("tolerance 必须是对象")
    default_tol = tolerance.get("default", {}) or {}
    if not isinstance(default_tol, dict):
        raise ValueError("tolerance.default 必须是对象")
    for name, rules in [("default", default_tol), *[(str(k), v) for k, v in tolerance.items() if k != "default"]]:
        if not isinstance(rules, dict):
            raise ValueError(f"tolerance.{name} 必须是对象")
        for field in ("absolute", "relative"):
            if field in rules and Decimal(str(rules[field])) < 0:
                raise ValueError(f"tolerance.{name}.{field} 不能为负数")
        if "round" in rules and (not isinstance(rules["round"], int) or not 0 <= rules["round"] <= 6):
            raise ValueError(f"tolerance.{name}.round 必须是 0 到 6 的整数")
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
                    rules = dict(default_tol)
                    rules.update(tolerance.get(column, {}) or {})
                    if "round" in rules:
                        places = int(rules["round"])
                        quantum = Decimal(1).scaleb(-places)
                        da, db = da.quantize(quantum, rounding=ROUND_HALF_UP), db.quantize(quantum, rounding=ROUND_HALF_UP)
                    delta_value = da - db
                    if delta_value == 0:
                        continue
                    absolute = Decimal(str(rules.get("absolute", "0")))
                    relative = Decimal(str(rules.get("relative", "0")))
                    threshold = max(absolute, max(abs(da), abs(db)) * relative)
                    if abs(delta_value) <= threshold:
                        differences.append({"key": key, "status": "within_tolerance", "column": column, "left_value": a, "right_value": b, "difference": str(delta_value), "tolerance": str(threshold)})
                        continue
                    if da == db:
                        continue
                    delta = str(delta_value)
            except (InvalidOperation, TypeError):
                pass
            differences.append({"key": key, "status": "mismatch", "left_table": config["left"], "right_table": config["right"], "left_row": left[key][0], "right_row": right[key][0], "column": column, "left_value": a, "right_value": b, "difference": delta})
    return {"left_rows": len(left), "right_rows": len(right), "differences": differences}
