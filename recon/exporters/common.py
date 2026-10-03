from pathlib import Path


def rows_from_result(result):
    return result.get("differences", []) if isinstance(result, dict) else []


def write_parent(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
