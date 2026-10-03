LEVELS = {"fatal": {"label": "致命", "exit_code": 2}, "serious": {"label": "严重", "exit_code": 1}, "notice": {"label": "提示", "exit_code": 0}}


def classify(row):
    status = row.get("status")
    if status in ("left_only", "right_only", "data_missing", "chain_mismatch"):
        return "fatal"
    if status in ("mismatch", "total_mismatch", "plugin_mismatch"):
        return "serious"
    return "notice" if status == "within_tolerance" else "notice"


def grade(rows):
    result = []
    for row in rows:
        level = classify(row)
        result.append({**row, "severity": level, "severity_label": LEVELS[level]["label"]})
    return result


def exit_code(rows):
    return 2 if any(classify(row) == "fatal" for row in rows) else 0


def summary(rows):
    graded = grade(rows)
    return {level: sum(item["severity"] == level for item in graded) for level in LEVELS}
