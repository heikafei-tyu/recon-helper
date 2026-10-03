import json
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, PlainTextResponse

from .engine import run_rules
from .history import load_history

app = FastAPI(title="recon-helper API", version="0.1.0")

PAGE = """<!doctype html><meta charset='utf-8'><title>recon-helper</title><style>body{font:15px system-ui;max-width:1000px;margin:2rem auto;color:#243047}nav a{margin-right:1rem}.fatal{color:#b91c1c;background:#fee2e2}.serious{color:#c2410c;background:#ffedd5}.hint{color:#a16207;background:#fef9c3}table{border-collapse:collapse;width:100%}td,th{padding:.5rem;border:1px solid #ddd}</style><nav><a href='/'>核对</a><a href='/web/history'>历史记录</a><a href='/web/reports'>报告下载</a></nav>{content}"""

def page(content):
    return HTMLResponse(PAGE.format(content=content))

@app.get("/", response_class=HTMLResponse)
def web_home():
    return page("<h1>上传与核对</h1><form action='/web/reconcile' method='post' enctype='multipart/form-data'><p>左表 <input type='file' name='left' required></p><p>右表 <input type='file' name='right' required></p><p>规则 YAML <input type='file' name='rules' required></p><button>执行核对</button></form>")

@app.post("/web/reconcile", response_class=HTMLResponse)
async def web_reconcile(left: UploadFile = File(...), right: UploadFile = File(...), rules: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / left.filename).write_bytes(await left.read()); (root / right.filename).write_bytes(await right.read())
        rule_bytes = await rules.read()
        config = json.loads(rule_bytes.decode("utf-8")) if rules.filename.endswith(".json") else __import__("yaml").safe_load(rule_bytes.decode("utf-8"))
        config["left"], config["right"] = left.filename, right.filename
        path = root / "rules.yaml"; path.write_text(__import__("yaml").safe_dump(config), encoding="utf-8")
        result = run_rules(path)
    rows = "".join(f"<tr class={'fatal' if r.get('status') in ('left_only','right_only','data_missing') else 'serious' if r.get('status') in ('mismatch','total_mismatch','chain_mismatch') else 'hint'}><td>{r.get('key','')}</td><td>{r.get('status','')}</td><td>{r.get('column','')}</td><td>{r.get('difference','')}</td></tr>" for r in result["differences"])
    return page(f"<h1>核对结果</h1><p>差异数：{len(result['differences'])}</p><table><tr><th>键</th><th>状态</th><th>列</th><th>差值</th></tr>{rows}</table>")

@app.get("/web/history", response_class=HTMLResponse)
def web_history():
    items = load_history()
    rows = "".join(f"<tr><td>{item.get('created_at','')}</td><td>{item.get('summary',{}).get('differences',0)}</td></tr>" for item in items)
    return page(f"<h1>历史记录</h1><table><tr><th>时间</th><th>差异数</th></tr>{rows}</table>")

@app.get("/web/reports", response_class=HTMLResponse)
def web_reports():
    return page("<h1>报告下载</h1><p>请使用命令行生成报告：</p><pre>recon report rules.yaml --out output/reconciliation.xlsx</pre><a href='/docs'>打开 API 文档</a>")

@app.post("/reconcile")
async def reconcile(file: UploadFile = File(...), rules: str = Form(...)):
    if not file.filename or Path(file.filename).suffix.lower() not in (".csv", ".xlsx", ".json"):
        raise HTTPException(status_code=400, detail={"code": "INVALID_FILE", "message": "仅支持 CSV/XLSX/JSON"})
    try:
        config = json.loads(rules)
        if not isinstance(config, dict): raise ValueError("rules 必须是对象")
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail={"code": "INVALID_RULES", "message": str(exc)}) from exc
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); data_path = root / file.filename; data_path.write_bytes(await file.read())
        config["left"] = file.filename
        config.setdefault("right", file.filename)
        rules_path = root / "rules.json"; rules_path.write_text(json.dumps(config), encoding="utf-8")
        try:
            return run_rules(rules_path)
        except (ValueError, OSError) as exc:
            raise HTTPException(status_code=422, detail={"code": "RECONCILE_ERROR", "message": str(exc)}) from exc

@app.get("/history")
def history(directory: str = "history"):
    return {"items": load_history(directory)}
