"""差异记录构造。"""
def missing_difference(key, side, row_number=None):
    return {"key": key[0] if len(key) == 1 else list(key), "status": f"{side}_only", f"{side}_row": row_number}


def value_difference(key, column, left, right, delta=None, **extra):
    item = {"key": key[0] if len(key) == 1 else list(key), "status": "mismatch", "column": column, "left_value": left, "right_value": right, "difference": delta}
    item.update(extra)
    return item
