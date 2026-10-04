"""规则语法层检查。"""


def check_syntax(raw):
    errors = []
    if not isinstance(raw, dict):
        return ["根节点必须是对象"]
    for key in ("left", "right", "columns"):
        if key not in raw:
            errors.append(f"缺少键：{key}")
    if "columns" in raw and (not isinstance(raw["columns"], list) or not raw["columns"]):
        errors.append("columns 类型必须是非空列表")
    return errors
