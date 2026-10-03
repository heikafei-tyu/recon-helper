from .common import rows_from_result, write_parent


def export_markdown(result, output):
    rows = rows_from_result(result)
    columns = sorted({key for row in rows for key in row}) or ["status"]
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    lines.extend("| " + " | ".join(str(row.get(key, "")).replace("|", "\\|") for key in columns) + " |" for row in rows)
    path = write_parent(output)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"output": str(path), "rows": len(rows), "format": "markdown"}
