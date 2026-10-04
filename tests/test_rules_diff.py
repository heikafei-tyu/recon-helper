import json
import pytest

from recon.cli import main
from recon.rules_diff import diff_rules


def test_diff_reports_added_removed_and_changed(tmp_path):
    old = tmp_path / "old.yaml"; new = tmp_path / "new.yaml"
    old.write_text("keys: [id]\ncolumns: [amount]\ntolerance: {amount: {absolute: 1}}\n", encoding="utf-8")
    new.write_text("keys: [code]\ncolumns: [amount, tax]\ntolerance: {amount: {absolute: 10}}\n", encoding="utf-8")
    result = diff_rules(old, new)
    assert result["summary"] == {"added": 1, "removed": 0, "changed": 2}
    assert any(item["path"] == "tolerance.amount.absolute" for item in result["changed"])


def test_diff_cli_outputs_json(tmp_path, capsys):
    old = tmp_path / "old.yaml"; new = tmp_path / "new.yaml"
    old.write_text("left: a.csv\n", encoding="utf-8"); new.write_text("left: b.csv\n", encoding="utf-8")
    assert main(["rules", "diff", str(old), str(new)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["summary"]["changed"] == 1


def test_diff_rejects_non_object(tmp_path):
    old = tmp_path / "old.yaml"; new = tmp_path / "new.yaml"
    old.write_text("- invalid\n", encoding="utf-8"); new.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="对象"):
        diff_rules(old, new)
