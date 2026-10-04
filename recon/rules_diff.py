"""Compare two YAML reconciliation rule versions."""

from pathlib import Path
from typing import Any

import yaml


def _load(path) -> dict:
    source = Path(path)
    try:
        data = yaml.safe_load(source.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        raise ValueError(f"无法读取规则文件：{source}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML 格式错误：{exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"规则文件必须是对象：{source}")
    return data


def _flatten(value: Any, prefix=""):
    if isinstance(value, dict):
        for key in sorted(value):
            path = f"{prefix}.{key}" if prefix else str(key)
            yield from _flatten(value[key], path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _flatten(item, f"{prefix}[{index}]")
    else:
        yield prefix, value


def diff_rules(old_path, new_path):
    old, new = _load(old_path), _load(new_path)
    before, after = dict(_flatten(old)), dict(_flatten(new))
    added = [{"path": key, "value": after[key]} for key in sorted(set(after) - set(before))]
    removed = [{"path": key, "value": before[key]} for key in sorted(set(before) - set(after))]
    changed = [
        {"path": key, "old": before[key], "new": after[key]}
        for key in sorted(set(before) & set(after))
        if before[key] != after[key]
    ]
    return {
        "old": str(old_path),
        "new": str(new_path),
        "added": added,
        "removed": removed,
        "changed": changed,
        "summary": {"added": len(added), "removed": len(removed), "changed": len(changed)},
    }
