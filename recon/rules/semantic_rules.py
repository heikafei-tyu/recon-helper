"""规则业务语义层检查。"""
def check_semantics(raw):
    errors = []
    tolerance = raw.get("tolerance", {}) if isinstance(raw, dict) else {}
    for name, item in tolerance.items() if isinstance(tolerance, dict) else []:
        items = item if isinstance(item, list) else [item]
        for rule in items:
            if isinstance(rule, dict) and any(float(rule.get(field, 0)) < 0 for field in ("absolute", "relative")):
                errors.append(f"tolerance.{name} 不能为负")
    return errors
