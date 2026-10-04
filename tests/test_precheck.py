"""precheck 自检脚本的单元测试。

注意：precheck.main() 的"测试全绿"检查会调用 pytest 子进程，
在 pytest 内直接调用会无限递归，因此这里用假 runner 替换 subprocess.run。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import precheck  # noqa: E402


class _FakeResult:
    returncode = 0
    stdout = "324 passed in 1.0s"
    stderr = ""


@pytest.fixture
def fake_runner(monkeypatch):
    """把 precheck 的 subprocess.run 替换为假结果，并清空累计的检查项。"""
    precheck.checks.clear()
    monkeypatch.setattr(precheck.subprocess, "run", lambda *a, **k: _FakeResult())


def test_precheck_all_pass_with_fake_runner(fake_runner):
    """假 runner 下全部自检项应通过（退出码 0）。"""
    code = precheck.main()
    assert code == 0
    for name, ok, detail in precheck.checks:
        assert ok, f"自检项未通过: {name} ({detail})"


def test_precheck_covers_core_items(fake_runner):
    """自检必须覆盖平台准入的核心项。"""
    precheck.main()
    names = [c[0] for c in precheck.checks]
    assert any("提交数量" in n for n in names)
    assert any("代码文件" in n for n in names)
    assert any("README" in n for n in names)
    assert any("密钥" in n for n in names)
    assert any("测试全绿" in n for n in names)


def test_changelog_exists_and_nonempty():
    """发布版本说明 CHANGELOG.md 应存在且非空。"""
    changelog = Path(__file__).resolve().parent.parent / "CHANGELOG.md"
    assert changelog.exists(), "CHANGELOG.md 缺失"
    assert changelog.read_text(encoding="utf-8").strip() != ""
