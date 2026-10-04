import io
import json
from fastapi.testclient import TestClient
from recon import api
from recon.store import ResultStore


def test_rule_editor_and_dashboard_pages(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    client = TestClient(api.app)
    assert client.get("/web/rules").status_code == 200
    response = client.post("/web/rules", data={"left": "left.csv", "right": "right.csv", "key": "id", "columns": "amount", "absolute": "0.01", "priority": "2"})
    assert response.status_code == 200 and "规则编辑器" in response.text
    assert client.get("/web/dashboard").status_code == 200


def test_reconcile_pagination(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    client = TestClient(api.app)
    rules = json.dumps({"key": "id", "columns": ["amount"]})
    csv = b"id,amount\nA001,1\nA002,2\n"
    response = client.post("/reconcile?page=1&page_size=1", files={"file": ("data.csv", io.BytesIO(csv), "text/csv")}, data={"rules": rules})
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1 and body["page_size"] == 1 and body["total_differences"] == 0


def test_history_date_filter_and_pagination(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with ResultStore(tmp_path / "recon_history.db") as store:
        store.save({}, {"differences": []})
    client = TestClient(api.app)
    response = client.get("/history?from_date=2000-01-01&to_date=2099-01-01&limit=1&offset=0")
    assert response.status_code == 200 and response.json()["total"] >= 1
