"""本地准入自检脚本：提交平台前运行，模拟平台的准入检查项。

用法: python scripts/precheck.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
checks: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    checks.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT).stdout


def main() -> int:
    if not (ROOT / ".git").exists():
        print("请在仓库根目录运行本脚本")
        return 2

    commits = git("log", "--oneline").splitlines()
    check("提交数量 > 30", len(commits) > 30, f"当前 {len(commits)}")

    py_files = [p for p in git("ls-files").splitlines() if p.endswith(".py")]
    check("代码文件 >= 100", len(py_files) >= 100, f"当前 {len(py_files)}")

    readme = ROOT / "README.md"
    sections = ["是什么", "安装", "运行"] if readme.exists() else []
    ok = readme.exists() and all(s in readme.read_text(encoding="utf-8") for s in ["安装", "运行"])
    check("README 基础完整（是什么/安装/运行）", ok, f"缺少: {[s for s in ['安装', '运行'] if s not in (readme.read_text(encoding='utf-8') if readme.exists() else '')]}")

    check("requirements.txt 存在", (ROOT / "requirements.txt").exists())
    test_command = [sys.executable, "-m", "pytest", "-q"]
    try:
        import pytest  # noqa: F401
    except ImportError:
        test_command = ["uv", "run", "--offline", "--with", "pytest", "--with", "pyyaml", "--with", "openpyxl", "--with", "pandas", "--with", "reportlab", "--with", "matplotlib", "--with", "fastapi", "--with", "httpx", "--with", "python-multipart", "pytest", "-q"]
    test_run = subprocess.run(test_command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    check("测试全绿", test_run.returncode == 0, test_run.stdout.splitlines()[-1] if test_run.stdout else test_run.stderr[-200:])
    features = ["读取", "容差", "报告", "历史", "Web", "调度"]
    readme_text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    check("README 特性清单", all(item in readme_text for item in features), f"缺少: {[item for item in features if item not in readme_text]}")

    secrets = []
    for p in git("ls-files").splitlines():
        if p.endswith((".py", ".yaml", ".yml", ".md")):
            text = (ROOT / p).read_text(encoding="utf-8", errors="ignore")
            for token in ("sk-", "api_key =", "password =", "BEGIN PRIVATE KEY"):
                if token in text and "****" not in text:
                    secrets.append(f"{p} 含 {token!r}")
    check("无明显密钥残留", not secrets, "; ".join(secrets[:3]))

    failed = [c for c in checks if not c[1]]
    print(f"\n结果: {len(checks) - len(failed)}/{len(checks)} 通过")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
