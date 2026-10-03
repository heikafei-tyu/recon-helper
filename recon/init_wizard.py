from pathlib import Path

import yaml


def build_rules(answers):
    return {"left": answers["left"], "right": answers["right"], "key": answers["key"], "columns": [item.strip() for item in answers["columns"].split(",") if item.strip()], "tolerance": {"default": {"absolute": answers["tolerance"]}}}


def run_wizard(output="rules.yaml", input_fn=input, print_fn=print):
    answers = {"left": input_fn("左表文件名: "), "right": input_fn("右表文件名: "), "key": input_fn("键列: "), "columns": input_fn("比较列（逗号分隔）: "), "tolerance": input_fn("绝对容差: ")}
    rules = build_rules(answers)
    print_fn(yaml.safe_dump(rules, allow_unicode=True, sort_keys=False))
    if input_fn("确认写入? [y/N]: ").lower() != "y":
        return {"saved": False, "rules": rules}
    path = Path(output); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(yaml.safe_dump(rules, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return {"saved": True, "output": str(path), "rules": rules}
