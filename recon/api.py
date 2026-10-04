import json
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from .config import load_config
from .engine import run_rules
from .history import load_history
from .notify import NotificationSettings, notify_result
from .operations import history_summary, review_queue
from .store import ResultStore

app = FastAPI(title="recon-helper API", version="0.1.0")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def render_template(name, values):
    text = (TEMPLATE_DIR / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    return HTMLResponse(text)


@app.middleware("http")
async def api_key_guard(request: Request, call_next):
    configured = os.getenv("RECON_API_KEY") or load_config().get("api_key")
    provided = request.headers.get("X-API-Key")
    if configured and provided != configured:
        status = 401
        response = PlainTextResponse("Unauthorized", status_code=status)
    else:
        response = await call_next(request)
        status = response.status_code
    with ResultStore() as store:
        store.audit(provided[:8] if provided else "anonymous", request.method, request.url.path, status)
    return response


PAGE = """<!doctype html><meta charset='utf-8'><title>recon-helper</title><link rel='stylesheet' href='/static/style.css'><nav><a href='/'>核对</a><a href='/web/history'>历史记录</a><a href='/web/reports'>报告下载</a></nav>{content}<script src='/static/app.js'></script>"""


def page(content):
    return HTMLResponse(PAGE.replace("{content}", content))


@app.get("/", response_class=HTMLResponse)
def web_home():
    return page(
        "<h1>上传与核对</h1><form action='/web/reconcile' method='post' enctype='multipart/form-data'><p>左表 <input type='file' name='left' required></p><p>右表 <input type='file' name='right' required></p><p>规则 YAML <input type='file' name='rules' required></p><button>执行核对</button></form>"
    )


@app.post("/web/reconcile", response_class=HTMLResponse)
async def web_reconcile(left: UploadFile = File(...), right: UploadFile = File(...), rules: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / left.filename).write_bytes(await left.read())
        (root / right.filename).write_bytes(await right.read())
        rule_bytes = await rules.read()
        config = (
            json.loads(rule_bytes.decode("utf-8"))
            if rules.filename.endswith(".json")
            else __import__("yaml").safe_load(rule_bytes.decode("utf-8"))
        )
        config["left"], config["right"] = left.filename, right.filename
        path = root / "rules.yaml"
        path.write_text(__import__("yaml").safe_dump(config), encoding="utf-8")
        result = run_rules(path)
    rows = "".join(
        f"<tr class={'fatal' if r.get('status') in ('left_only', 'right_only', 'data_missing') else 'serious' if r.get('status') in ('mismatch', 'total_mismatch', 'chain_mismatch') else 'hint'}><td>{r.get('key', '')}</td><td>{r.get('status', '')}</td><td>{r.get('column', '')}</td><td>{r.get('difference', '')}</td></tr>"
        for r in result["differences"]
    )
    return page(
        f"<h1>核对结果</h1><p>差异数：{len(result['differences'])}</p><a href='/web/reports'>导出本次报告</a><table><tr><th data-sort>键</th><th data-sort>状态</th><th data-sort>列</th><th data-sort>差值</th></tr>{rows}</table>"
    )


@app.get("/web/history", response_class=HTMLResponse)
def web_history(from_date: str | None = None, to_date: str | None = None):
    items = load_history()
    if from_date:
        items = [item for item in items if item.get("created_at", "")[:10] >= from_date]
    if to_date:
        items = [item for item in items if item.get("created_at", "")[:10] <= to_date]
    rows = "".join(
        f"<tr><td>{item.get('created_at', '')}</td><td>{item.get('summary', {}).get('differences', 0)}</td></tr>"
        for item in items
    )
    return page(
        f"<h1>历史记录</h1><form><input type='date' name='from_date'><input type='date' name='to_date'><button>筛选</button></form><table><tr><th>时间</th><th>差异数</th></tr>{rows}</table>"
    )


@app.get("/web/reports", response_class=HTMLResponse)
def web_reports():
    return page(
        "<h1>报告下载</h1><p>请使用命令行生成报告：</p><pre>recon report rules.yaml --out output/reconciliation.xlsx</pre><a href='/docs'>打开 API 文档</a>"
    )


@app.get("/web/rules", response_class=HTMLResponse)
def web_rules(request: Request):
    return render_template(
        "rules_editor.html",
        {
            "left": "left.csv",
            "right": "right.csv",
            "key": "id",
            "columns": "amount",
            "absolute": "0.01",
            "priority": "0",
            "errors_html": "",
            "saved_html": "",
        },
    )


@app.post("/web/rules", response_class=HTMLResponse)
async def save_web_rules(
    request: Request,
    left: str = Form(...),
    right: str = Form(...),
    key: str = Form(...),
    columns: str = Form(...),
    absolute: str = Form(""),
    priority: str = Form("0"),
):
    import yaml

    values = {
        "left": left,
        "right": right,
        "key": key,
        "columns": [item.strip() for item in columns.split(",") if item.strip()],
        "tolerance": {"default": {"absolute": absolute or "0", "priority": int(priority or 0)}},
    }
    errors = []
    if not values["columns"]:
        errors.append("至少填写一个比较列")
    try:
        values["tolerance"]["default"]["priority"] = int(priority or 0)
    except ValueError:
        errors.append("优先级必须是整数")
    if not key.strip():
        errors.append("键列不能为空")
    draft_dir = Path("rules-drafts")
    draft_dir.mkdir(exist_ok=True)
    path = draft_dir / "rules.yaml"
    path.write_text(yaml.safe_dump(values, allow_unicode=True), encoding="utf-8")
    if not errors:
        from .rules import validate_rules

        errors.extend(validate_rules(path))
    errors_html = (
        "<section class='errors'><h2>校验错误</h2><ul>"
        + "".join(f"<li>{error}</li>" for error in errors)
        + "</ul></section>"
        if errors
        else ""
    )
    saved_html = (
        "" if errors else f"<p class='success'>规则已保存：{path}</p><pre>{path.read_text(encoding='utf-8')}</pre>"
    )
    return render_template(
        "rules_editor.html",
        {
            "left": left,
            "right": right,
            "key": key,
            "columns": columns,
            "absolute": absolute,
            "priority": priority,
            "errors_html": errors_html,
            "saved_html": saved_html,
        },
    )


@app.get("/web/dashboard", response_class=HTMLResponse)
def web_dashboard(request: Request):
    with ResultStore() as store:
        items = store.query(limit=1000)
    recent_rows = "".join(
        f"<tr><td>{item['id']}</td><td>{item['created_at']}</td><td>{item['severity']}</td><td>{item['difference_count']}</td></tr>"
        for item in items[:10]
    )
    return render_template(
        "dashboard.html",
        {
            "total": len(items),
            "differences": sum(item["difference_count"] for item in items),
            "recent_rows": recent_rows,
        },
    )


@app.get("/dashboard/summary")
def dashboard_summary():
    return history_summary()


@app.get("/review-queue")
def review_queue_endpoint(limit: int = Query(100, ge=1, le=1000)):
    return review_queue(limit=limit)


@app.get("/batches")
def batches(limit: int = Query(100, ge=1, le=1000)):
    with ResultStore() as store:
        return {"items": store.batches(limit)}


@app.post("/reconcile")
async def reconcile(
    file: UploadFile = File(...),
    rules: str = Form(...),
    notify_webhook: str | None = Form(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
):
    if not file.filename or Path(file.filename).suffix.lower() not in (".csv", ".xlsx", ".json"):
        raise HTTPException(status_code=400, detail={"code": "INVALID_FILE", "message": "仅支持 CSV/XLSX/JSON"})
    try:
        config = json.loads(rules)
        if not isinstance(config, dict):
            raise ValueError("rules 必须是对象")
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail={"code": "INVALID_RULES", "message": str(exc)}) from exc
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        data_path = root / file.filename
        data_path.write_bytes(await file.read())
        config["left"] = file.filename
        config.setdefault("right", file.filename)
        rules_path = root / "rules.json"
        rules_path.write_text(json.dumps(config), encoding="utf-8")
        try:
            result = run_rules(rules_path)
            with ResultStore() as store:
                history_id = store.save(
                    config, result, {file.filename: __import__("hashlib").sha256(data_path.read_bytes()).hexdigest()}
                )
            if notify_webhook:
                result["notification"] = notify_result(
                    result, NotificationSettings(webhook_url=notify_webhook, enabled=True)
                )
            result["history_id"] = history_id
            result["total_differences"] = len(result["differences"])
            start = (page - 1) * page_size
            result["page"] = page
            result["page_size"] = page_size
            result["differences"] = result["differences"][start : start + page_size]
            return result
        except (ValueError, OSError) as exc:
            raise HTTPException(status_code=422, detail={"code": "RECONCILE_ERROR", "message": str(exc)}) from exc


@app.get("/history")
def history(
    directory: str = "history",
    from_date: str | None = None,
    to_date: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    items = load_history(directory)
    if from_date:
        items = [item for item in items if item.get("created_at", "")[:10] >= from_date]
    if to_date:
        items = [item for item in items if item.get("created_at", "")[:10] <= to_date]
    return {"items": items[offset : offset + limit], "total": len(items)}


@app.post("/history/{history_id}/review")
def review_history(history_id: int, status: str = Form(...), note: str = Form("")):
    with ResultStore() as store:
        return store.review(history_id, status, note)


@app.get("/reports/{history_id}")
def download_history_report(history_id: int):
    with ResultStore() as store:
        items = [item for item in store.query() if item["id"] == history_id]
    if not items:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    return JSONResponse(
        items[0], headers={"Content-Disposition": f"attachment; filename=reconciliation-{history_id}.json"}
    )
