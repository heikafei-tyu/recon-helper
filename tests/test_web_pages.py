import json
import pytest

httpx = pytest.importorskip("httpx")
from recon.api import app


@pytest.mark.anyio
async def test_web_pages():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/")).status_code == 200
        assert "上传与核对" in (await client.get("/")).text
        assert "历史记录" in (await client.get("/web/history")).text
        assert "报告下载" in (await client.get("/web/reports")).text


@pytest.mark.anyio
async def test_web_reconcile_form():
    transport = httpx.ASGITransport(app=app)
    rules = "key: id\ncolumns: [amount]\n"
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/web/reconcile", files={"left": ("l.csv", b"id,amount\na,1\n"), "right": ("r.csv", b"id,amount\na,1\n"), "rules": ("rules.yaml", rules.encode())})
    assert response.status_code == 200 and "差异数" in response.text
