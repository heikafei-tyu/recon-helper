import json

import pytest

httpx = pytest.importorskip("httpx")
from recon.api import app


@pytest.mark.anyio
async def test_reconcile_api():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("x.csv", b"id,amount\na,1\n", "text/csv")}
        rules = {"key": "id", "columns": ["amount"]}
        response = await client.post("/reconcile", files=files, data={"rules": json.dumps(rules)})
    assert response.status_code == 200
    assert response.json()["differences"] == []

@pytest.mark.anyio
async def test_reconcile_api_rejects_bad_input():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/reconcile", files={"file": ("x.exe", b"bad")}, data={"rules": "{}"})
    assert response.status_code == 400
