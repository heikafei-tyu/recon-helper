import json

from recon.cli import main


def test_plan_cli_runs_config(tmp_path, capsys):
    left = tmp_path / "left.csv"; right = tmp_path / "right.csv"
    left.write_text("id,v\na,1\n", encoding="utf-8")
    right.write_text("id,v\na,1\n", encoding="utf-8")
    rules = tmp_path / "rules.yaml"
    rules.write_text("left: left.csv\nright: right.csv\nkey: id\ncolumns: [v]\n", encoding="utf-8")
    plan = tmp_path / "plan.yaml"
    plan.write_text("tasks:\n  - name: daily\n    rules: rules.yaml\n", encoding="utf-8")
    assert main(["plan", str(plan)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["execution"]["daily"]["status"] == "success"


def test_plan_cli_retries_invalid_rule_and_fail_fast(tmp_path, capsys):
    plan = tmp_path / "plan.yaml"
    plan.write_text("tasks:\n  - name: broken\n    rules: missing.yaml\n  - name: skipped\n    rules: missing2.yaml\n", encoding="utf-8")
    assert main(["plan", str(plan), "--attempts", "2", "--fail-fast"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["stopped"] is True
    assert payload["execution"]["broken"]["attempts"] == 2
