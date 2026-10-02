import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill

from .engine import run_rules


def _digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def create_report(rules_file, output, incremental=False, force=False):
    rules_path = Path(rules_file)
    output = Path(output)
    import yaml
    config = yaml.safe_load(rules_path.read_text(encoding="utf-8-sig"))
    sources = [rules_path, rules_path.parent / config["left"], rules_path.parent / config["right"]]
    manifest = {str(p): _digest(p) for p in sources if p.exists()}
    marker = output.with_suffix(output.suffix + ".manifest.json")
    if output.exists() and not incremental and not force:
        raise ValueError(f"报告已存在：{output}；如需覆盖请使用 --force")
    if incremental and output.exists() and marker.exists() and json.loads(marker.read_text()) == manifest:
        try:
            existing = load_workbook(output, read_only=True)
            valid = {"Differences", "Summary"}.issubset(existing.sheetnames)
            existing.close()
        except Exception:
            valid = False
        if valid:
            return {"output": str(output), "skipped": True}
    result = run_rules(rules_file)
    book = Workbook()
    sheet = book.active
    sheet.title = "Differences"
    rows = result["differences"]
    preferred = ["key", "status", "left_table", "right_table", "left_row", "right_row", "column", "left_value", "right_value", "difference", "tolerance", "tolerance_type", "tolerance_rule", "rule_priority"]
    columns = [key for key in preferred if any(key in row for row in rows)] or ["status"]
    sheet.append(columns)
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = f"A1:{chr(64 + min(len(columns), 26))}{len(rows) + 1}"
    fills = {"mismatch": PatternFill("solid", fgColor="FFC7CE"), "within_tolerance": PatternFill("solid", fgColor="FFF2CC"), "left_only": PatternFill("solid", fgColor="FCE4D6"), "right_only": PatternFill("solid", fgColor="FCE4D6")}
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    for row in rows:
        sheet.append([" / ".join(row[k]) if isinstance(row.get(k), (tuple, list)) else row.get(k) for k in columns])
        fill = fills.get(row.get("status"))
        if fill:
            for cell in sheet[sheet.max_row]:
                cell.fill = fill
    for column_cells in sheet.columns:
        letter = column_cells[0].column_letter
        sheet.column_dimensions[letter].width = min(40, max(12, max(len(str(cell.value or "")) for cell in column_cells) + 2))
    summary = book.create_sheet("Summary")
    summary.append(["metric", "value"])
    counts = {status: sum(r.get("status") == status for r in rows) for status in ("mismatch", "within_tolerance", "left_only", "right_only")}
    summary_rows = [("tool_version", "0.1.0"), ("run_at_utc", datetime.now(timezone.utc).isoformat()), ("rules_file", str(rules_path)), ("left_file", str(sources[1])), ("right_file", str(sources[2])), ("left_sha256", manifest.get(str(sources[1]))), ("right_sha256", manifest.get(str(sources[2]))), ("left_rows", result["left_rows"]), ("right_rows", result["right_rows"]), ("differences", len(rows)), *counts.items()]
    for key, value in summary_rows:
        summary.append([key, value])
    summary.freeze_panes = "A2"
    output.parent.mkdir(parents=True, exist_ok=True)
    book.save(output)
    marker.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"output": str(output), "skipped": False, "differences": len(rows)}
