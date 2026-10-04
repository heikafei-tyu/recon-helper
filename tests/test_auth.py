import pytest

httpx = pytest.importorskip("httpx")
from recon.api import app
from recon.store import ResultStore


@pytest.mark.anyio
async def test_api_key_auth_and_audit(tmp_path, monkeypatch):
    monkeypatch.setenv("RECON_API_KEY", "secret")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        denied = await client.get("/history")
        allowed = await client.get("/history", headers={"X-API-Key": "secret"})
    assert denied.status_code == 401 and allowed.status_code == 200
    with ResultStore() as store:
        assert any(item["status"] == 401 for item in store.audits())
