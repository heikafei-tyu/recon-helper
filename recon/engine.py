"""按 YAML 指定的唯一键和字段比较两张表。"""
import time
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from .config import load_rule_config
from .filters import matches
from .finance_checks import run_finance_checks
from .numbers import normalize_number
from .readers import read_table
from .transforms import transform
from .units import convert_amount, normalize_date


def run_rules(filename, timeout=None, progress=False):
    if timeout is not None and timeout < 0:
        raise ValueError("timeout 不能为负数")
    started = time.perf_counter()

    def check_deadline(processed=0, total=None):
        if timeout is not None and time.perf_counter() - started > timeout:
            raise TimeoutError(f"超过 {timeout} 秒")
        if progress and processed and (processed % 1000 == 0 or processed == total):
            percent = processed / total * 100 if total else 0
            print(f"processed_rows={processed} progress={percent:.1f}%")

    rule_config = load_rule_config(filename)
    path = rule_config.source
    config = rule_config.raw
    if "checks" in config:
        check_deadline()
        return {"left_rows": 0, "right_rows": 0, "differences": run_finance_checks(path.parent, config["checks"])}
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
    key_mapping = config.get("key_mapping", {}) or {}
    left_keys = key_mapping.get("left", keys)
    right_keys = key_mapping.get("right", keys)
    if not all(isinstance(names, list) and len(names) == len(keys) and all(isinstance(name, str) and name for name in names) for names in (left_keys, right_keys)):
        raise ValueError("key_mapping.left/right 必须与 keys 等长的字段列表")
    columns = config["columns"]
    if not isinstance(columns, list) or not columns:
        raise ValueError("columns 必须是非空字段列表")
    mappings = [(c, c) if isinstance(c, str) else (c.get("left"), c.get("right")) for c in columns]
    if any(not left_name or not right_name for left_name, right_name in mappings):
        raise ValueError("比较字段必须是字符串或包含 left/right 的对象")
    if len({pair for pair in mappings}) != len(mappings):
        raise ValueError("比较字段不能重复")
    normalize = config.get("normalize", {}) or {}
    if not isinstance(normalize, dict):
        raise ValueError("normalize 必须是对象")
    trim = bool(normalize.get("trim", False))
    casefold = bool(normalize.get("casefold", False))
    null_policy = config.get("null_policy", "different")
    if null_policy not in ("equal", "different"):
        raise ValueError("null_policy 必须是 equal 或 different")

    def clean(value):
        if value is None:
            return None
        value = str(value)
        if trim:
            value = value.strip()
        if casefold:
            value = value.casefold()
        return value
    tolerance = config.get("tolerance", {})
    if tolerance is None:
        tolerance = {}
    if not isinstance(tolerance, dict):
        raise ValueError("tolerance 必须是对象")
    default_tol = tolerance.get("default", {}) or {}
    if not isinstance(default_tol, dict):
        raise ValueError("tolerance.default 必须是对象")
    for name, configured in [("default", default_tol), *[(str(k), v) for k, v in tolerance.items() if k != "default"]]:
        rule_list = configured if isinstance(configured, list) else [configured]
        if not rule_list or not all(isinstance(r, dict) for r in rule_list):
            raise ValueError(f"tolerance.{name} 必须是对象或对象列表")
        for rules in rule_list:
            for field in ("absolute", "relative"):
                if field in rules:
                    try:
                        value = Decimal(str(rules[field]))
                    except InvalidOperation as exc:
                        raise ValueError(f"tolerance.{name}.{field} 必须是数字") from exc
                    if not value.is_finite() or value < 0:
                        raise ValueError(f"tolerance.{name}.{field} 必须是非负有限数字")
            if "round" in rules and (not isinstance(rules["round"], int) or not 0 <= rules["round"] <= 6):
                raise ValueError(f"tolerance.{name}.round 必须是 0 到 6 的整数")
            rounding = rules.get("rounding")
            if rounding is not None:
                if not isinstance(rounding, dict) or rounding.get("mode", "raw") not in ("raw", "cents", "decimal"):
                    raise ValueError(f"tolerance.{name}.rounding.mode 必须是 raw、cents 或 decimal")
                if "digits" in rounding and (not isinstance(rounding["digits"], int) or not 0 <= rounding["digits"] <= 6):
                    raise ValueError(f"tolerance.{name}.rounding.digits 必须是 0 到 6 的整数")
            if "priority" in rules and (not isinstance(rules["priority"], int) or rules["priority"] < 0):
                raise ValueError(f"tolerance.{name}.priority 必须是非负整数")
    tables = [read_table(path.parent / config[side], sheet_name=config.get(f"{side}_sheet")) for side in ("left", "right")]
    total_rows = sum(len(table.rows) for table in tables)
    indexes = []
    for table in tables:
        table_keys = left_keys if table is tables[0] else right_keys
        required = list(table_keys) + ([pair[0] for pair in mappings] if table is tables[0] else [pair[1] for pair in mappings])
        for column in required:
            if column not in table.columns:
                raise ValueError(f"输入缺少字段 {column}")
        key_columns = table_keys
        key_indexes = [table.columns.index(column) for column in key_columns]
        index = {}
        for number, row in enumerate(table.rows, 2):
            check_deadline(number - 1, total_rows)
            record = dict(zip(table.columns, row))
            filter_conditions = config.get("filters", {}).get("left" if table is tables[0] else "right", [])
            if not matches(record, filter_conditions):
                continue
            key = tuple(clean(row[index]) for index in key_indexes)
            if any(value is None or not str(value).strip() for value in key) or key in index:
                raise ValueError(f"第 {number} 行关联键为空或重复")
            index[key] = (number, dict(zip(table.columns, row)))
        indexes.append(index)
    left, right = indexes
    differences = []
    for key in sorted(left.keys() | right.keys()):
        display_key = key[0] if len(key) == 1 else list(key)
        if key not in left or key not in right:
            differences.append({"key": display_key, "status": "left_only" if key in left else "right_only", "left_row": left[key][0] if key in left else None, "right_row": right[key][0] if key in right else None})
            continue
        for left_column, right_column in mappings:
            column = left_column
            operations = config.get("transforms", {}).get(left_column, [])
            a = transform(clean(left[key][1][left_column]), operations)
            b = transform(clean(right[key][1][right_column]), operations)
            units = config.get("units", {}) or {}
            if left_column in units or right_column in units:
                setting = units.get(left_column, units.get(right_column, {}))
                a = str(convert_amount(a, setting.get("left", "元"), setting.get("target", "元"), setting.get("rates")))
                b = str(convert_amount(b, setting.get("right", "元"), setting.get("target", "元"), setting.get("rates")))
            dates = config.get("dates", {}) or {}
            if dates.get(left_column) or dates.get(right_column):
                a, b = normalize_date(a), normalize_date(b)
            if a is None or b is None:
                if a is None and b is None and null_policy == "equal":
                    continue
                differences.append({"key": display_key, "status": "mismatch", "column": column, "left_value": a, "right_value": b, "difference": None})
                continue
            if a == b:
                continue
            delta = None
            try:
                da, db = normalize_number(a), normalize_number(b)
                if da.is_finite() and db.is_finite():
                    configured = tolerance.get(column, {}) or {}
                    candidates = configured if isinstance(configured, list) else [configured]
                    candidates = [dict(default_tol, **candidate) for candidate in candidates]
                    candidates.sort(key=lambda item: item.get("priority", 0), reverse=True)
                    matched = False
                    ignored_rules = []
                    for rules in candidates:
                        rule_da, rule_db = da, db
                        rounding = rules.get("rounding", {}) or {}
                        rounding_mode = rounding.get("mode", "raw") if isinstance(rounding, dict) else "raw"
                        digits = rounding.get("digits", 2) if isinstance(rounding, dict) else rules.get("round")
                        if "round" in rules:
                            rounding_mode, digits = "decimal", rules["round"]
                        if rounding_mode in ("cents", "decimal"):
                            quantum = Decimal(1).scaleb(-int(digits))
                            rule_da, rule_db = rule_da.quantize(quantum, rounding=ROUND_HALF_UP), rule_db.quantize(quantum, rounding=ROUND_HALF_UP)
                        delta_value = rule_da - rule_db
                        if delta_value == 0:
                            matched = True
                            break
                        absolute_limit = Decimal(str(rules.get("absolute", "0")))
                        relative_limit = max(abs(rule_da), abs(rule_db)) * Decimal(str(rules.get("relative", "0")))
                        threshold = max(absolute_limit, relative_limit)
                        if abs(delta_value) <= threshold:
                            method = "absolute" if absolute_limit >= relative_limit else "relative"
                            differences.append({"key": display_key, "status": "within_tolerance", "column": column, "left_value": a, "right_value": b, "difference": str(delta_value), "tolerance": str(threshold), "tolerance_type": method, "tolerance_rule": rules.get("name", column), "relative_base": str(max(abs(rule_da), abs(rule_db))), "rule_priority": rules.get("priority", 0), "rounding_mode": rounding_mode, "ignored_rules": [item.get("name", column) for item in ignored_rules]})
                            matched = True
                            break
                        ignored_rules.append(rules)
                    if matched:
                        continue
                    delta = str(da - db)
            except (InvalidOperation, TypeError, ValueError):
                pass
            differences.append({"key": display_key, "status": "mismatch", "left_table": config["left"], "right_table": config["right"], "left_row": left[key][0], "right_row": right[key][0], "column": column, "left_value": a, "right_value": b, "difference": delta})
    return {"left_rows": len(left), "right_rows": len(right), "differences": differences}
