"""核对结果摘要。"""

from collections import Counter


def _counts(differences, field):
    """Count explicit values without turning missing metadata into ``None`` buckets."""
    return dict(Counter(item[field] for item in differences if item.get(field) is not None))


def summarize(differences, left_rows, right_rows):
    if left_rows < 0 or right_rows < 0:
        raise ValueError("行数不能为负数")
    differences = list(differences)
    compared_rows = max(left_rows, right_rows)
    mismatch_count = sum(item.get("status") == "mismatch" for item in differences)
    return {
        "left_rows": left_rows,
        "right_rows": right_rows,
        "differences": differences,
        "difference_count": len(differences),
        "conclusion": "通过" if not differences else "存在差异",
        "status_counts": _counts(differences, "status"),
        "severity_counts": _counts(differences, "severity"),
        "matched_rows": max(compared_rows - mismatch_count, 0),
        "difference_rate": (len(differences) / compared_rows if compared_rows else 0.0),
    }
