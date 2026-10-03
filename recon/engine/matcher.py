"""匹配阶段的可复用键处理工具。"""
def make_key(row, columns, clean=str):
    values = tuple(clean(row.get(column)) for column in columns)
    if any(value is None or not str(value).strip() for value in values):
        raise ValueError("关联键不能为空")
    return values


def match_rows(rows, columns, clean=str):
    result = {}
    for number, row in enumerate(rows, 2):
        key = make_key(row, columns, clean)
        if key in result:
            raise ValueError("关联键重复")
        result[key] = (number, row)
    return result
