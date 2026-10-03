import json
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from .engine import run_rules
from .history import load_history

app = FastAPI(title="recon-helper API", version="0.1.0")

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
