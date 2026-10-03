def check(left, right, rule):
    """检查两侧关键值是否为空。"""
    return [{"status": "plugin_mismatch", "index": index} for index, (a, b) in enumerate(zip(left, right)) if a in (None, "") or b in (None, "")]
