import json

from recon.cli import main


def test_plan_cli_runs_config(tmp_path, capsys):
    left = tmp_path / "left.csv"
    right = tmp_path / "right.csv"
    left.write_text("id,v\na,1\n", encoding="utf-8")
    right.write_text("id,v\na,1\n", encoding="utf-8")
    rules = tmp_path / "rules.yaml"
    rules.write_text("left: left.csv\nright: right.csv\nkey: id\ncolumns: [v]\n", encoding="utf-8")
    plan = tmp_path / "plan.yaml"
    plan.write_text("tasks:\n  - name: daily\n    rules: rules.yaml\n", encoding="utf-8")
    assert main(["plan", str(plan)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["execution"]["daily"]["status"] == "success"


def test_plan_cli_explicit_run_form(tmp_path, capsys):
    plan = tmp_path / "plan.yaml"
    plan.write_text("tasks: []\n", encoding="utf-8")
    assert main(["plan", "run", str(plan)]) == 2
    assert "ERROR" in capsys.readouterr().err


def test_plan_cli_retries_invalid_rule_and_fail_fast(tmp_path, capsys):
    plan = tmp_path / "plan.yaml"
    plan.write_text(
        "tasks:\n  - name: broken\n    rules: missing.yaml\n  - name: skipped\n    rules: missing2.yaml\n",
        encoding="utf-8",
    )
    assert main(["plan", str(plan), "--attempts", "2", "--fail-fast"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["stopped"] is True
    assert payload["execution"]["broken"]["attempts"] == 2


def test_plan_cli_persists_run_and_idempotency(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "left.csv").write_text("id,v\na,1\n", encoding="utf-8")
    (tmp_path / "right.csv").write_text("id,v\na,1\n", encoding="utf-8")
    (tmp_path / "rules.yaml").write_text("left: left.csv\nright: right.csv\nkey: id\ncolumns: [v]\n", encoding="utf-8")
    (tmp_path / "plan.yaml").write_text("tasks:\n  - name: daily\n    rules: rules.yaml\n", encoding="utf-8")
    assert main(["plan", str(tmp_path / "plan.yaml"), "--idempotency-key", "daily-1"]) == 0
    first = json.loads(capsys.readouterr().out)
    assert first["run_id"] == 1
    assert main(["plan", str(tmp_path / "plan.yaml"), "--idempotency-key", "daily-1"]) == 0
    second = json.loads(capsys.readouterr().out)
    assert second["run_id"] == 1


def test_plan_parallel_layer_runs_all_tasks(tmp_path, capsys):
    for name in ("a", "b"):
        (tmp_path / f"{name}.csv").write_text("id,v\na,1\n", encoding="utf-8")
    for name in ("a", "b"):
        (tmp_path / f"{name}.yaml").write_text(f"left: {name}.csv\nright: {name}.csv\nkey: id\ncolumns: [v]\n", encoding="utf-8")
    plan = tmp_path / "plan.yaml"
    plan.write_text("tasks:\n  - name: a\n    rules: a.yaml\n  - name: b\n    rules: b.yaml\n", encoding="utf-8")
    assert main(["plan", str(plan), "--workers", "2"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert {payload["execution"][key]["status"] for key in ("a", "b")} == {"success"}
