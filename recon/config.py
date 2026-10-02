from dataclasses import dataclass
from pathlib import Path

import yaml

from .errors import RuleConfigError


@dataclass(frozen=True)
class RuleConfig:
    source: Path
    left: str
    right: str
    raw: dict


def load_rule_config(filename):
    source = Path(filename)
    try:
        raw = yaml.safe_load(source.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        raise RuleConfigError(f"无法读取规则文件：{source}") from exc
    except yaml.YAMLError as exc:
        raise RuleConfigError(f"YAML 格式错误：{exc}") from exc
    if not isinstance(raw, dict):
        raise RuleConfigError("规则必须是对象")
    for name in ("left", "right"):
        if not isinstance(raw.get(name), str) or not raw[name].strip():
            raise RuleConfigError(f"{name} 必须是非空路径")
    return RuleConfig(source, raw["left"], raw["right"], raw)
