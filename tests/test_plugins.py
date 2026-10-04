import pytest

from recon.plugins import discover_plugins, run_plugin


def test_discover_and_run_example_plugins():
    plugins = discover_plugins()
    assert {"amount_range", "nonempty"}.issubset(plugins)
    assert run_plugin("amount_range", [10, 20], [10, 18], {"limit": 1})[0]["difference"] == 2
    assert run_plugin("nonempty", [1, ""], [1, 2])[0]["index"] == 1


def test_custom_plugin_discovery(tmp_path):
    (tmp_path / "custom.py").write_text(
        "def check(left, right, rule):\n    return [{'status': 'ok'}]\n", encoding="utf-8"
    )
    assert run_plugin("custom", [], [], directory=tmp_path) == [{"status": "ok"}]


@pytest.mark.parametrize("name", ["missing", "", "unknown"])
def test_missing_plugin(name):
    with pytest.raises(ValueError):
        run_plugin(name, [], [])


def test_invalid_plugin_signature(tmp_path):
    (tmp_path / "bad.py").write_text("def check(one):\n    return []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="check"):
        discover_plugins(tmp_path)
