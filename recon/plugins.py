"""用户自定义核对插件发现与执行。"""
import importlib.util
import inspect
from pathlib import Path


def discover_plugins(directory="plugins"):
    root = Path(directory)
    found = {}
    if not root.exists():
        return found
    for path in sorted(root.glob("*.py")):
        if path.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(f"recon_plugin_{path.stem}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        check = getattr(module, "check", None)
        if not callable(check) or len(inspect.signature(check).parameters) != 3:
            raise ValueError(f"插件 {path} 必须提供 check(left, right, rule)")
        found[path.stem] = check
    return found


def run_plugin(name, left, right, rule=None, directory="plugins"):
    plugins = discover_plugins(directory)
    if name not in plugins:
        raise ValueError(f"未找到插件：{name}")
    result = plugins[name](left, right, rule or {})
    if not isinstance(result, list):
        raise ValueError(f"插件 {name} 必须返回列表")
    return result
