"""Runtime health checks exposed by ``recon doctor``."""

import importlib
import importlib.metadata
import locale
import shutil
import sqlite3
import sys
from pathlib import Path

from .config import load_config

REQUIRED = {
    "yaml": "PyYAML",
    "openpyxl": "openpyxl",
    "pandas": "pandas",
    "xlrd": "xlrd",
    "pyarrow": "pyarrow",
}


def _check(name, passed, detail):
    return {"check": name, "status": "PASS" if passed else "FAIL", "detail": str(detail)}


def doctor(root=None, db_path=None):
    """Run non-destructive checks and return a machine-readable report."""
    root = Path(root or Path.cwd())
    checks = []
    checks.append(_check("python", sys.version_info >= (3, 10), sys.version.split()[0]))
    missing = []
    for module, package in REQUIRED.items():
        try:
            importlib.import_module(module)
            importlib.metadata.version(package)
        except (ImportError, importlib.metadata.PackageNotFoundError):
            missing.append(package)
    checks.append(_check("dependencies", not missing, "ok" if not missing else "missing: " + ", ".join(missing)))
    encoding = locale.getpreferredencoding(False)
    normalized_encoding = encoding.replace("-", "").upper()
    windows_legacy = sys.platform == "win32" and normalized_encoding in {"CP936", "GBK", "GB2312"}
    checks.append(_check("encoding", normalized_encoding in {"UTF8", "UTF8SIG"} or windows_legacy, encoding))
    usage = shutil.disk_usage(root)
    checks.append(_check("disk", usage.free >= 100 * 1024 * 1024, f"free_bytes={usage.free}"))
    try:
        config = load_config(root)
        workers = config.get("parallel_workers")
        if workers is not None and (not isinstance(workers, int) or isinstance(workers, bool) or workers < 1):
            raise ValueError("parallel_workers 必须是正整数")
        if config.get("report_template") not in {"simple", "detailed", "management"}:
            raise ValueError("report_template 必须是 simple、detailed 或 management")
        try:
            tolerance = float(config.get("default_tolerance", "0"))
        except (TypeError, ValueError) as exc:
            raise ValueError("default_tolerance 必须是非负数字") from exc
        if tolerance < 0:
            raise ValueError("default_tolerance 必须是非负数字")
        if not isinstance(config.get("output_dir"), str) or not config["output_dir"].strip():
            raise ValueError("output_dir 必须是非空字符串")
        checks.append(_check("config", True, config.get("config_file") or "defaults"))
    except Exception as exc:
        checks.append(_check("config", False, exc))
    rules_broken = []
    for rules_path in sorted(root.glob("examples/scenarios/*/rules.yaml")) + sorted(root.glob("rules.yaml")):
        try:
            import yaml

            data = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or "rules" not in data:
                rules_broken.append(f"{rules_path.parent.name}: 缺少 rules 键")
        except Exception as exc:
            rules_broken.append(f"{rules_path.parent.name}: {exc}")
    checks.append(_check("rules_files", not rules_broken, "ok" if not rules_broken else "; ".join(rules_broken[:3])))
    out_dir = root / "reports"
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        probe = out_dir / ".doctor_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        checks.append(_check("output_writable", True, str(out_dir)))
    except Exception as exc:
        checks.append(_check("output_writable", False, exc))
    database = Path(db_path or root / "recon_history.db")
    if database.exists():
        try:
            with sqlite3.connect(database) as conn:
                result = conn.execute("PRAGMA integrity_check").fetchone()[0]
            checks.append(_check("history_db", result == "ok", result))
        except sqlite3.DatabaseError as exc:
            checks.append(_check("history_db", False, exc))
    else:
        checks.append(_check("history_db", True, "not created yet"))
    return {
        "ok": all(item["status"] == "PASS" for item in checks),
        "checks": checks,
        "table": [[item["check"], item["status"], item["detail"]] for item in checks],
    }
