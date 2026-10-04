from fastapi.testclient import TestClient

from recon import api
from recon.store import ResultStore


def test_batches_endpoint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with ResultStore(tmp_path / "recon_history.db") as store:
        store.create_batch("manual", [])
    response = TestClient(api.app).get("/batches")
    assert response.status_code == 200 and response.json()["items"][0]["name"] == "manual"
