import io
import json

import pytest
from fastapi.testclient import TestClient

from recon import api


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return TestClient(api.app)


def _payload():
    rules = json.dumps({"key": "id", "columns": ["amount"]})
    return {"file": ("data.csv", io.BytesIO(b"id,amount\nA001,10\n"), "text/csv"), "rules": (None, rules)}


def test_upload_review_and_report_download(client):
    response = client.post("/reconcile", files=_payload())
    assert response.status_code == 200
    history_id = response.json()["history_id"]
    review = client.post(f"/history/{history_id}/review", data={"status": "已确认无误", "note": "已复核"})
    assert review.status_code == 200 and review.json()["updated"] == 0
    report = client.get(f"/reports/{history_id}")
    assert report.status_code == 200 and "attachment" in report.headers["content-disposition"]


def test_upload_reconcile_triggers_webhook(client, monkeypatch):
    calls = []

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    monkeypatch.setattr(
        api,
        "notify_result",
        lambda result, settings: calls.append({"event": "reconciliation.completed"}) or {"sent": True},
    )
    response = client.post("/reconcile", files=_payload(), data={"notify_webhook": "https://example.test/hook"})
    assert response.status_code == 200
    assert calls[0]["event"] == "reconciliation.completed"


def test_incremental_report_skips_unchanged_input(client, tmp_path):
    from recon.report import create_report

    left = tmp_path / "left.csv"
    right = tmp_path / "right.csv"
    rules = tmp_path / "rules.yaml"
    left.write_text("id,amount\nA001,10\n", encoding="utf-8")
    right.write_text("id,amount\nA001,10\n", encoding="utf-8")
    rules.write_text("left: left.csv\nright: right.csv\nkey: id\ncolumns: [amount]\n", encoding="utf-8")
    output = tmp_path / "report.xlsx"
    assert create_report(rules, output, force=True)["skipped"] is False
    assert create_report(rules, output, incremental=True)["skipped"] is True
