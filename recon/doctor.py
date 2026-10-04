"""Runtime health checks exposed by ``recon doctor``."""
import importlib
import importlib.metadata
import shutil
import sqlite3
import sys
from pathlib import Path
import locale

from .config import load_config

REQUIRED = {"yaml": "PyYAML", "openpyxl": "openpyxl", "pandas": "pandas"}


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
    checks.append(_check("encoding", encoding.upper() in {"UTF-8", "UTF8"}, encoding))
    usage = shutil.disk_usage(root)
    checks.append(_check("disk", usage.free >= 100 * 1024 * 1024, f"free_bytes={usage.free}"))
    try:
        config = load_config(root)
        checks.append(_check("config", True, config.get("config_file") or "defaults"))
    except Exception as exc:
        checks.append(_check("config", False, exc))
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
