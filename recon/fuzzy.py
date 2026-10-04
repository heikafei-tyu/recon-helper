def distance(a, b):
    row = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        old, row[0] = row[0], i
        for j, right in enumerate(b, 1):
            current = row[j]
            row[j] = min(row[j] + 1, row[j - 1] + 1, old + (left != right))
            old = current
    return row[-1]


def match_column(name, candidates, max_distance=2):
    if not isinstance(name, str) or not name:
        raise ValueError("列名必须是非空字符串")
    scored = sorted((distance(name, item), item) for item in candidates)
    if not scored or scored[0][0] > max_distance:
        return None
    return {"name": scored[0][1], "distance": scored[0][0], "candidates": scored}


def match_columns(names, candidates, max_distance=2):
    return {name: match_column(name, candidates, max_distance) for name in names}


def similarity(left, right):
    size = max(len(left), len(right))
    return 1.0 if size == 0 else 1 - distance(left, right) / size


def best_column(name, candidates):
    return min(candidates, key=lambda value: distance(name, value)) if candidates else None
