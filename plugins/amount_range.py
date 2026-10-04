def check(left, right, rule):
    """检查两组金额差异是否超过插件自定义阈值。"""
    limit = float(rule.get("limit", 0))
    return [
        {"status": "plugin_mismatch", "difference": float(a) - float(b)}
        for a, b in zip(left, right)
        if abs(float(a) - float(b)) > limit
    ]
