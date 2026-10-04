"""YAML 对账规则的结构、引用和业务约束校验。"""

from pathlib import Path

import yaml


def validate_rules(filename):
    path = Path(filename)
    errors = []
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, yaml.YAMLError) as exc:
        return [f"规则文件不可读取：{exc}"]
    if not isinstance(raw, dict):
        return ["根节点必须是对象"]
    for key in ("left", "right", "columns"):
        if key not in raw:
            errors.append(f"缺少键：{key}")
    for key in ("left", "right"):
        if key in raw and (not isinstance(raw[key], str) or not raw[key].strip()):
            errors.append(f"{key} 类型必须是非空字符串")
    if "columns" in raw and (not isinstance(raw["columns"], list) or not raw["columns"]):
        errors.append("columns 类型必须是非空列表")
    keys = raw.get("keys", [raw.get("key")] if "key" in raw else [])
    if not isinstance(keys, list) or not keys or any(not isinstance(item, str) or not item for item in keys):
        errors.append("key/keys 必须是非空字符串列表")
    if len(set(keys)) != len(keys):
        errors.append("keys 不能重复")
    for side in ("left", "right"):
        sheet_key = f"{side}_sheet"
        if sheet_key in raw and (not isinstance(raw[sheet_key], str) or not raw[sheet_key].strip()):
            errors.append(f"{sheet_key} 必须是非空字符串")
    left_path, right_path = (path.parent / raw.get(key, "") for key in ("left", "right"))
    for label, source in (("left", left_path), ("right", right_path)):
        if raw.get(label) and not source.exists():
            errors.append(f"{label} 文件不存在：{raw[label]}")
    columns = raw.get("columns", [])
    names = []
    for index, column in enumerate(columns):
        if isinstance(column, str):
            names.append((column, column))
        elif isinstance(column, dict) and isinstance(column.get("left"), str) and isinstance(column.get("right"), str):
            names.append((column["left"], column["right"]))
        else:
            errors.append(f"columns[{index}] 必须是字符串或 left/right 对象")
    if len(set(names)) != len(names):
        errors.append("columns 不能重复")
    tolerance = raw.get("tolerance", {})
    if tolerance is not None and not isinstance(tolerance, dict):
        errors.append("tolerance 必须是对象")
    for name, configured in tolerance.items() if isinstance(tolerance, dict) else []:
        rules = configured if isinstance(configured, list) else [configured]
        if not all(isinstance(item, dict) for item in rules):
            errors.append(f"tolerance.{name} 必须是对象或对象列表")
            continue
        for item in rules:
            tiers = item.get("tiers")
            if tiers is not None:
                if not isinstance(tiers, list) or not tiers:
                    errors.append(f"tolerance.{name}.tiers 必须是非空列表")
                else:
                    previous = None
                    for index, tier in enumerate(tiers):
                        if not isinstance(tier, dict) or "absolute" not in tier:
                            errors.append(f"tolerance.{name}.tiers[{index}] 缺少 absolute")
                            continue
                        try:
                            absolute = float(tier["absolute"])
                            upper = None if tier.get("up_to") is None else float(tier["up_to"])
                            if absolute < 0:
                                errors.append(f"tolerance.{name}.tiers[{index}].absolute 不能为负")
                            if upper is not None and upper <= 0:
                                errors.append(f"tolerance.{name}.tiers[{index}].up_to 必须为正数")
                            if previous is not None and upper is not None and upper <= previous:
                                errors.append(f"tolerance.{name}.tiers 区间重叠或金额倒挂")
                            if previous is not None and upper is None and index != len(tiers) - 1:
                                errors.append(f"tolerance.{name}.tiers 无上限档位必须放在最后")
                            previous = upper if upper is not None else previous
                        except (TypeError, ValueError):
                            errors.append(f"tolerance.{name}.tiers[{index}] 数值格式错误")
                    if tiers[-1].get("up_to") is not None:
                        errors.append(f"tolerance.{name}.tiers 存在边界缺口：最后一档必须无上限")
            for field in ("absolute", "relative"):
                if field in item:
                    try:
                        if float(item[field]) < 0:
                            errors.append(f"tolerance.{name}.{field} 不能为负")
                    except (TypeError, ValueError):
                        errors.append(f"tolerance.{name}.{field} 必须是数字")
            if "priority" in item and (not isinstance(item["priority"], int) or item["priority"] < 0):
                errors.append(f"tolerance.{name}.priority 必须是非负整数")
            rounding = item.get("rounding")
            if rounding is not None and (
                not isinstance(rounding, dict) or rounding.get("mode") not in ("raw", "cents", "decimal")
            ):
                errors.append(f"tolerance.{name}.rounding.mode 非法")
            if isinstance(rounding, dict) and (
                "digits" in rounding and (not isinstance(rounding["digits"], int) or rounding["digits"] < 0)
            ):
                errors.append(f"tolerance.{name}.rounding.digits 非法")
    if "filters" in raw and not isinstance(raw["filters"], dict):
        errors.append("filters 必须是对象")
    if "transforms" in raw and not isinstance(raw["transforms"], dict):
        errors.append("transforms 必须是对象")
    checks = raw.get("checks")
    if checks is not None and not isinstance(checks, list):
        errors.append("checks 必须是列表")
    if isinstance(checks, list):
        for index, check in enumerate(checks):
            if not isinstance(check, dict) or check.get("type") not in ("total_check", "chain_check", "missing_check"):
                errors.append(f"checks[{index}] 类型未知")
            if isinstance(check, dict) and check.get("type") == "chain_check":
                tables = check.get("tables")
                if not isinstance(tables, list) or len(tables) < 2 or len(set(tables)) != len(tables):
                    errors.append(f"checks[{index}].tables 存在循环或数量不足")
    return errors
