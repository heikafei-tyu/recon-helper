"""Project-level .reconrc configuration."""

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
    if "checks" not in raw:
        for name in ("left", "right"):
            if not isinstance(raw.get(name), str) or not raw[name].strip():
                raise RuleConfigError(f"{name} 必须是非空路径")
    return RuleConfig(source, raw.get("left", ""), raw.get("right", ""), raw)


DEFAULTS = {
    "default_tolerance": "0",
    "parallel_workers": None,
    "output_dir": "output",
    "report_template": "detailed",
    "api_key": None,
}


def load_config(start=None):
    root = Path(start or Path.cwd())
    path = root / ".reconrc"
    values = dict(DEFAULTS)
    if path.exists():
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        if data is None:
            data = {}
        if not isinstance(data, dict):
            raise ValueError(".reconrc 必须是 YAML 对象")
        values.update({key: value for key, value in data.items() if key in DEFAULTS})
    values["config_file"] = str(path) if path.exists() else None
    return values
