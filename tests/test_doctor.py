import json

from recon.cli import main
from recon.doctor import doctor


def test_doctor_reports_required_environment_checks(tmp_path):
    result = doctor(tmp_path)
    names = {item["check"] for item in result["checks"]}
    assert names == {
        "python",
        "dependencies",
        "encoding",
        "disk",
        "config",
        "rules_files",
        "output_writable",
        "history_db",
    }
    assert all(item["status"] in {"PASS", "FAIL"} for item in result["checks"])


def test_doctor_detects_invalid_config(tmp_path):
    (tmp_path / ".reconrc").write_text("[]", encoding="utf-8")
    result = doctor(tmp_path)
    config = next(item for item in result["checks"] if item["check"] == "config")
    assert config["status"] == "FAIL"


def test_doctor_detects_invalid_config_value(tmp_path):
    (tmp_path / ".reconrc").write_text("report_template: unknown", encoding="utf-8")
    result = doctor(tmp_path)
    config = next(item for item in result["checks"] if item["check"] == "config")
    assert config["status"] == "FAIL"
    assert "report_template" in config["detail"]


def test_doctor_detects_corrupt_history_database(tmp_path):
    db = tmp_path / "recon_history.db"
    db.write_bytes(b"not a sqlite database")
    result = doctor(tmp_path, db_path=db)
    history = next(item for item in result["checks"] if item["check"] == "history_db")
    assert history["status"] == "FAIL"


def test_doctor_cli_returns_failure_for_failed_check(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".reconrc").write_text("report_template: invalid", encoding="utf-8")
    assert main(["doctor"]) == 1


def test_doctor_cli_outputs_json(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(["doctor"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert "checks" in report
