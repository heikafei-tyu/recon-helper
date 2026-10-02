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
    for field in ("left", "right", "columns"):
        if field not in config:
            raise ValueError(f"规则缺少 {field}")
    if not all(isinstance(config[f], str) and config[f] for f in ("left", "right")):
        raise ValueError("left/right 必须是非空字符串")
    keys = config.get("keys", [config["key"]] if isinstance(config.get("key"), str) else None)
    if not isinstance(keys, list) or not keys or not all(isinstance(k, str) and k for k in keys):
        raise ValueError("key 或 keys 必须是非空字段名")
    columns = config["columns"]
    if not isinstance(columns, list) or not columns:
        raise ValueError("columns 必须是非空字段列表")
    mappings = [(c, c) if isinstance(c, str) else (c.get("left"), c.get("right")) for c in columns]
    if any(not left_name or not right_name for left_name, right_name in mappings):
        raise ValueError("比较字段必须是字符串或包含 left/right 的对象")
    if len({pair for pair in mappings}) != len(mappings):
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
        required = list(keys) if table is tables[0] else [pair[1] for pair in mappings]
        required += [pair[0] for pair in mappings] if table is tables[0] else []
        for column in required:
            if column not in table.columns:
                raise ValueError(f"输入缺少字段 {column}")
        key_columns = keys if table is tables[0] else [keys[i] for i in range(len(keys))]
        key_indexes = [table.columns.index(column) for column in key_columns]
        index = {}
        for number, row in enumerate(table.rows, 2):
            key = tuple(row[index] for index in key_indexes)
            if any(value is None or not str(value).strip() for value in key) or key in index:
                raise ValueError(f"第 {number} 行关联键为空或重复")
            index[key] = (number, dict(zip(table.columns, row)))
        indexes.append(index)
    left, right = indexes
    differences = []
    for key in sorted(left.keys() | right.keys()):
        if key not in left or key not in right:
            differences.append({"key": key, "status": "left_only" if key in left else "right_only", "left_row": left[key][0] if key in left else None, "right_row": right[key][0] if key in right else None})
            continue
        for left_column, right_column in mappings:
            column = left_column
            a, b = left[key][1][left_column], right[key][1][right_column]
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
