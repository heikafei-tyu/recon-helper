"""Interactive rule-file generator with backwards-compatible prompts."""

from pathlib import Path

import yaml

RULE_TYPES = ("row_compare", "total_check", "chain_check", "period_check")


def _columns(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def build_rules(answers):
    """Build a validated YAML-compatible mapping from wizard answers."""
    kind = answers.get("type", answers.get("rule_type", "row_compare")) or "row_compare"
    if kind not in RULE_TYPES:
        raise ValueError(f"未知规则类型：{kind}")
    if kind == "row_compare":
        left = answers.get("left", "")
        right = answers.get("right", "")
        key = answers.get("key", "")
        columns = _columns(answers.get("columns", ""))
        if not left or not right or not key or not columns:
            raise ValueError("行比较规则需要 left、right、key 和 columns")
        rules = {"left": left, "right": right, "key": key, "columns": columns}
        absolute = str(answers.get("tolerance", answers.get("absolute", "0"))).strip()
        if absolute:
            rules["tolerance"] = {"default": {"absolute": absolute}}
        relative = str(answers.get("relative", "")).strip()
        if relative:
            rules["tolerance"]["default"]["relative"] = relative
        return rules
    if kind == "total_check":
        required = ("detail", "summary")
        if any(not answers.get(name) for name in required) or not _columns(answers.get("columns", "")):
            raise ValueError("total_check 需要明细、汇总和列名")
        return {
            "checks": [
                {
                    "type": kind,
                    "detail": answers["detail"],
                    "summary": answers["summary"],
                    "columns": _columns(answers["columns"]),
                }
            ]
        }
    if kind == "chain_check":
        tables = _columns(answers.get("tables", ""))
        if len(tables) < 2 or not answers.get("start_column") or not answers.get("end_column"):
            raise ValueError("chain_check 至少需要两张表、期初列和期末列")
        return {
            "checks": [
                {
                    "type": kind,
                    "tables": tables,
                    "start_column": answers["start_column"],
                    "end_column": answers["end_column"],
                }
            ]
        }
    required = ("file", "period_column", "value_column", "current", "previous")
    if any(not answers.get(name) for name in required):
        raise ValueError("period_check 需要文件、期间列、数值列、当前期和上一期")
    threshold = str(answers.get("threshold", "0.3"))
    return {
        "checks": [
            {
                "type": kind,
                "file": answers["file"],
                "period_column": answers["period_column"],
                "value_column": answers["value_column"],
                "current": answers["current"],
                "previous": answers["previous"],
                "threshold": threshold,
            }
        ]
    }


def _ask(input_fn, print_fn, label, history):
    value = input_fn(label).strip()
    if value.lower() in {"back", "上一步"} and history:
        return history.pop(), True
    return value, False


def run_wizard(output="rules.yaml", input_fn=input, print_fn=print):
    """Run the wizard; ``input_fn`` and ``print_fn`` make it testable."""
    history = []
    answers = {}
    prompts = [
        ("left", "左表文件名: "),
        ("right", "右表文件名: "),
        ("key", "键列: "),
        ("columns", "比较列（逗号分隔）: "),
        ("tolerance", "绝对容差: "),
    ]
    index = 0
    while index < len(prompts):
        name, label = prompts[index]
        value, went_back = _ask(input_fn, print_fn, label, history)
        if went_back:
            index = max(0, index - 1)
            continue
        answers[name] = value
        history.append(name)
        index += 1

    # Keeping y/n here preserves the original five-answer API used by scripts.
    kind = input_fn("规则类型 [row_compare/total_check/chain_check/period_check]（默认 row_compare）: ").strip()
    if kind.lower() in {"y", "n"}:
        confirmation = kind.lower()
        kind = "row_compare"
    else:
        confirmation = None
    answers["type"] = kind or "row_compare"
    if answers["type"] == "total_check":
        answers["detail"] = input_fn("明细文件: ").strip()
        answers["summary"] = input_fn("汇总文件: ").strip()
        answers["columns"] = input_fn("合计列（逗号分隔）: ").strip()
    elif answers["type"] == "chain_check":
        answers["tables"] = input_fn("表文件（逗号分隔）: ").strip()
        answers["start_column"] = input_fn("期初列: ").strip()
        answers["end_column"] = input_fn("期末列: ").strip()
    elif answers["type"] == "period_check":
        for name, label in (
            ("file", "数据文件: "),
            ("period_column", "期间列: "),
            ("value_column", "数值列: "),
            ("current", "当前期间: "),
            ("previous", "上一期间: "),
            ("threshold", "波动比例（默认 0.3）: "),
        ):
            answers[name] = input_fn(label).strip() or ("0.3" if name == "threshold" else "")
    rules = build_rules(answers)
    preview = yaml.safe_dump(rules, allow_unicode=True, sort_keys=False)
    print_fn("规则预览：\n" + preview)
    if confirmation is None:
        confirmation = input_fn("确认写入? [y/N]（输入 back 可返回修改）: ").strip().lower()
        if confirmation in {"back", "上一步"}:
            print_fn("请重新运行向导并修改上一项。")
            return {"saved": False, "rules": rules, "back": True}
    if confirmation != "y":
        return {"saved": False, "rules": rules}
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(preview, encoding="utf-8")
    return {"saved": True, "output": str(path), "rules": rules}
