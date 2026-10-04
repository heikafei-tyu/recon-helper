from fastapi.testclient import TestClient
from recon import api
from recon.store import ResultStore


def test_operations_api(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with ResultStore(tmp_path / "recon_history.db") as store:
        store.save({}, {"differences": [{"status": "mismatch"}]})
    client = TestClient(api.app)
    summary = client.get("/dashboard/summary")
    queue = client.get("/review-queue?limit=10")
    assert summary.status_code == 200 and summary.json()["total_runs"] == 1
    assert queue.status_code == 200 and queue.json()["total"] == 1
