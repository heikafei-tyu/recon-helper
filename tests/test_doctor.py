import json

from recon.cli import main
from recon.doctor import doctor


def test_doctor_reports_required_environment_checks(tmp_path):
    result = doctor(tmp_path)
    names = {item["check"] for item in result["checks"]}
    assert names == {"python", "dependencies", "encoding", "disk", "config", "history_db"}
    assert all(item["status"] in {"PASS", "FAIL"} for item in result["checks"])


def test_doctor_detects_invalid_config(tmp_path):
    (tmp_path / ".reconrc").write_text("[]", encoding="utf-8")
    result = doctor(tmp_path)
    config = next(item for item in result["checks"] if item["check"] == "config")
    assert config["status"] == "FAIL"


def test_doctor_cli_outputs_json(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(["doctor"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert "checks" in report
