"""重复行检测。"""
from collections import defaultdict


def find_duplicates(rows, keys=None):
    groups = defaultdict(list)
    for index, row in enumerate(rows):
        record = dict(row)
        key = tuple(record.get(name) for name in keys) if keys else tuple(sorted(record.items()))
        groups[key].append(index)
    return [{"key": list(key), "rows": indexes, "count": len(indexes)} for key, indexes in groups.items() if len(indexes) > 1]


def duplicate_summary(rows, keys=None):
    groups = find_duplicates(rows, keys)
    return {"groups": groups, "duplicate_rows": sum(item["count"] for item in groups), "group_count": len(groups)}

def duplicate_key(row, keys=None):
    record = dict(row)
    return tuple(record.get(name) for name in keys) if keys else tuple(sorted(record.items()))

def iter_duplicate_groups(rows, keys=None):
    yield from find_duplicates(rows, keys)

def has_duplicates(rows, keys=None):
    return bool(find_duplicates(rows, keys))
