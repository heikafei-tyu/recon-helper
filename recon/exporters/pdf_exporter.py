from .common import rows_from_result, write_parent


def export_pdf(result, output):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    except ImportError as exc:
        raise RuntimeError("PDF 导出需要安装 reportlab") from exc
    rows = rows_from_result(result)
    columns = sorted({key for row in rows for key in row}) or ["status"]
    data = [columns] + [[str(row.get(key, "")) for key in columns] for row in rows]
    path = write_parent(output)
    document = SimpleDocTemplate(str(path), pagesize=A4)
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
            ]
        )
    )
    document.build([table])
    return {"output": str(path), "rows": len(rows), "format": "pdf"}
