"""可复用的规则配置 Profile。"""

import json
from pathlib import Path

PROFILES = {
    "strict": {"name": "严格模式", "tolerance": {"default": {"absolute": "0"}}, "rules": {"allow_missing": False}},
    "宽松": {
        "name": "宽松模式",
        "tolerance": {"default": {"absolute": "0.01", "relative": "0.005"}},
        "rules": {"allow_missing": True},
    },
}


def list_profiles():
    return [{"id": key, **value} for key, value in PROFILES.items()]


def show_profile(profile):
    try:
        return {"id": profile, **PROFILES[profile]}
    except KeyError as exc:
        raise ValueError(f"未知 profile：{profile}") from exc


def use_profile(profile, output):
    data = show_profile(profile)
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"profile": profile, "output": str(path)}
