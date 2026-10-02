import hashlib
import json
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill
from .engine import run_rules

def _digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def create_report(rules_file, output, incremental=False):
    rules_path = Path(rules_file)
    output = Path(output)
    sources = [rules_path, rules_path.parent / "orders.csv", rules_path.parent / "bank.csv"]
    manifest = {str(p): _digest(p) for p in sources if p.exists()}
    marker = output.with_suffix(output.suffix + ".manifest.json")
    if incremental and output.exists() and marker.exists() and json.loads(marker.read_text()) == manifest:
        return {"output": str(output), "skipped": True}
    result = run_rules(rules_file)
    book = Workbook()
    sheet = book.active
    sheet.title = "Differences"
    rows = result["differences"]
    columns = sorted({k for row in rows for k in row}) if rows else ["status"]
    sheet.append(columns)
    red = PatternFill("solid", fgColor="FFC7CE")
    for row in rows:
        sheet.append([row.get(k) for k in columns])
        if row.get("status") == "mismatch":
            for cell in sheet[sheet.max_row]: cell.fill = red
    summary = book.create_sheet("Summary")
    summary.append(["metric", "value"])
    for key, value in [("left_rows", result["left_rows"]), ("right_rows", result["right_rows"]), ("differences", len(rows)), ("mismatches", sum(r.get("status") == "mismatch" for r in rows))]: summary.append([key, value])
    output.parent.mkdir(parents=True, exist_ok=True)
    book.save(output)
    marker.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"output": str(output), "skipped": False, "differences": len(rows)}
