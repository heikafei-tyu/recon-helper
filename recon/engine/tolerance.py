"""统一的 Decimal 容差决策与审计结果。"""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


def within_tolerance(left, right, absolute=0, relative=0):
    left, right = Decimal(str(left)), Decimal(str(right))
    delta = abs(left - right)
    threshold = max(Decimal(str(absolute)), max(abs(left), abs(right)) * Decimal(str(relative)))
    return delta <= threshold, delta, threshold


def decide(left, right, rules=None):
    """按优先级选择第一条命中的规则，并返回完整决策对象。"""
    try:
        left_value, right_value = Decimal(str(left)), Decimal(str(right))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("容差比较值必须是数字") from exc
    if not left_value.is_finite() or not right_value.is_finite():
        raise ValueError("容差比较值必须是有限数字")
    candidates = rules or [{}]
    if not isinstance(candidates, list) or not all(isinstance(item, dict) for item in candidates):
        raise ValueError("容差规则必须是对象列表")
    ordered = sorted(candidates, key=lambda item: item.get("priority", 0), reverse=True)
    ignored = []
    last_threshold = Decimal("0")
    for configured in ordered:
        rule = dict(configured)
        band = None
        if "tiers" in rule:
            tiers = rule["tiers"]
            if not isinstance(tiers, list) or not tiers:
                raise ValueError("容差档位必须是非空列表")
            amount = max(abs(left_value), abs(right_value))
            selected = tiers[-1]
            for tier in tiers:
                if not isinstance(tier, dict) or "absolute" not in tier:
                    raise ValueError("容差档位必须包含 absolute")
                upper = tier.get("up_to")
                if upper is None or amount <= Decimal(str(upper)):
                    selected = tier
                    break
            band = selected.get("name", selected.get("up_to", "以上"))
            rule.update(selected)
        mode = rule.get("rounding", {}).get("mode", "raw") if isinstance(rule.get("rounding", {}), dict) else "raw"
        digits = rule.get("rounding", {}).get("digits", 2) if isinstance(rule.get("rounding", {}), dict) else 2
        if "round" in rule:
            mode, digits = "decimal", rule["round"]
        if mode not in ("raw", "cents", "decimal"):
            raise ValueError("舍入模式必须是 raw、cents 或 decimal")
        if not isinstance(digits, int) or not 0 <= digits <= 6:
            raise ValueError("舍入位数必须是 0 到 6 的整数")
        compared_left, compared_right = left_value, right_value
        if mode in ("cents", "decimal"):
            quantum = Decimal(1).scaleb(-digits)
            compared_left = compared_left.quantize(quantum, rounding=ROUND_HALF_UP)
            compared_right = compared_right.quantize(quantum, rounding=ROUND_HALF_UP)
        difference = compared_left - compared_right
        absolute = Decimal(str(rule.get("absolute", 0)))
        relative = Decimal(str(rule.get("relative", 0)))
        if absolute < 0 or relative < 0:
            raise ValueError("容差必须是非负数")
        threshold = max(absolute, max(abs(compared_left), abs(compared_right)) * relative)
        last_threshold = max(last_threshold, threshold)
        if difference == 0 or abs(difference) <= threshold:
            return {"matched": True, "difference": str(difference), "threshold": str(threshold), "tolerance_type": "absolute" if absolute >= max(abs(compared_left), abs(compared_right)) * relative else "relative", "tolerance_rule": rule.get("name", "default"), "tolerance_band": band, "rule_priority": rule.get("priority", 0), "rounding_mode": mode, "rounding_digits": digits, "ignored_rules": [item.get("name", "default") for item in ignored]}
        ignored.append(rule)
    return {"matched": False, "difference": str(left_value - right_value), "threshold": str(last_threshold), "ignored_rules": [item.get("name", "default") for item in ignored]}
