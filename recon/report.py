import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill

from .engine import run_rules


def create_html_report(rules_file, output):
    result = run_rules(rules_file)
    rows = result["differences"]
    columns = ["key", "status", "column", "left_value", "right_value", "difference"]
    header = "".join(f"<th>{column}</th>" for column in columns)
    body = "".join("<tr>" + "".join(f"<td>{str(row.get(column, '')).replace('&', '&amp;').replace('<', '&lt;')}</td>" for column in columns) + "</tr>" for row in rows)
    html = f"<!doctype html><meta charset='utf-8'><title>recon-helper report</title><table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    return {"output": str(output), "differences": len(rows)}


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
    source_names = [config.get("left"), config.get("right")]
    for check in config.get("checks", []):
        source_names.extend([check.get("detail"), check.get("summary"), check.get("file")])
        source_names.extend(check.get("tables", []))
    sources = [rules_path, *[rules_path.parent / name for name in source_names if name]]
    sources = list(dict.fromkeys(sources))
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
    summary = book.active
    summary.title = "Summary"
    rows = result["differences"]
    preferred = ["key", "status", "left_table", "right_table", "left_row", "right_row", "column", "left_value", "right_value", "difference", "tolerance", "tolerance_type", "tolerance_rule", "rule_priority"]
    columns = [key for key in preferred if any(key in row for row in rows)] or ["status"]
    def add_detail_sheet(title, selected):
        sheet = book.create_sheet(title)
        sheet.append(columns)
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = f"A1:{chr(64 + min(len(columns), 26))}{len(selected) + 1}"
        fills = PatternFill("solid", fgColor="FFF2CC")
        for cell in sheet[1]:
            cell.font = Font(bold=True)
        for row in selected:
            sheet.append([" / ".join(row[k]) if isinstance(row.get(k), (tuple, list)) else row.get(k) for k in columns])
            if row.get("status") in ("mismatch", "total_mismatch", "chain_mismatch", "data_missing", "left_only", "right_only"):
                for cell in sheet[sheet.max_row]:
                    cell.fill = fills
        for column_cells in sheet.columns:
            letter = column_cells[0].column_letter
            sheet.column_dimensions[letter].width = min(40, max(12, max(len(str(cell.value or "")) for cell in column_cells) + 2))
        return sheet

    add_detail_sheet("Differences", rows)
    detail_names = []
    for name in source_names:
        if not name:
            continue
        title = Path(name).stem[:25] or "table"
        if title in {"Summary", "Differences"} or title in detail_names:
            title = f"{title}_{len(detail_names) + 1}"
        detail_names.append(title)
        selected = [row for row in rows if Path(str(row.get("left_table", ""))).stem == Path(name).stem or Path(str(row.get("right_table", ""))).stem == Path(name).stem or row.get("from") == name or row.get("to") == name]
        add_detail_sheet(title, selected)
    summary.append(["metric", "value"])
    counts = {status: sum(r.get("status") == status for r in rows) for status in ("mismatch", "within_tolerance", "left_only", "right_only")}
    summary_rows = [("tool_version", "0.1.0"), ("run_at_utc", datetime.now(timezone.utc).isoformat()), ("rules_file", str(rules_path)), ("left_file", str(sources[1]) if len(sources) > 1 else None), ("right_file", str(sources[2]) if len(sources) > 2 else None), ("left_sha256", manifest.get(str(sources[1])) if len(sources) > 1 else None), ("right_sha256", manifest.get(str(sources[2])) if len(sources) > 2 else None), ("left_rows", result.get("left_rows", 0)), ("right_rows", result.get("right_rows", 0)), ("differences", len(rows)), ("conclusion", "通过" if not rows else "存在差异"), *counts.items()]
    for key, value in summary_rows:
        summary.append([key, value])
    summary.freeze_panes = "A2"
    output.parent.mkdir(parents=True, exist_ok=True)
    book.save(output)
    marker.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"output": str(output), "skipped": False, "differences": len(rows)}
