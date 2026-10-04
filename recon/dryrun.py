"""Explain one row-compare rule without persisting or producing a report."""
from pathlib import Path
from .config import load_rule_config
from .numbers import normalize_number
from .readers import read_table


def dry_run(rule_file):
    config = load_rule_config(rule_file).raw
    if "checks" in config:
        raise ValueError("dryrun 只支持单条左右表规则")
    source = Path(rule_file).parent
    left = read_table(source / config["left"])
    right = read_table(source / config["right"])
    keys = config.get("keys") or [config.get("key")]
    if not keys or any(key not in left.columns or key not in right.columns for key in keys):
        raise ValueError("dryrun 的键列必须同时存在于左右表")
    columns = config.get("columns", [])
    mappings = [(item, item) if isinstance(item, str) else (item["left"], item["right"]) for item in columns]
    def index(table):
        positions = [table.columns.index(key) for key in keys]
        return {tuple(row[pos] for pos in positions): row for row in table.rows}
    left_index, right_index = index(left), index(right)
    steps = []
    for key in sorted(left_index.keys() | right_index.keys()):
        if key not in left_index or key not in right_index:
            steps.append({"key": key[0] if len(key) == 1 else list(key), "step": "match", "matched": False, "reason": "left_only" if key in left_index else "right_only"})
            continue
        left_row, right_row = left_index[key], right_index[key]
        for left_col, right_col in mappings:
            a, b = left_row[left.columns.index(left_col)], right_row[right.columns.index(right_col)]
            normalized = {"left": a, "right": b}
            delta = None
            try: delta = str(normalize_number(a) - normalize_number(b))
            except (TypeError, ValueError, ArithmeticError): pass
            steps.append({"key": key[0] if len(key) == 1 else list(key), "step": "compare", "column": left_col, "raw": {"left": a, "right": b}, "normalized": normalized, "difference": delta, "equal": a == b})
    return {"rule": str(rule_file), "tables": {"left": left.summary(), "right": right.summary()}, "matched_keys": [key[0] if len(key) == 1 else list(key) for key in sorted(left_index.keys() & right_index.keys())], "steps": steps}
