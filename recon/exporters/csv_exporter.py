import csv

from .common import rows_from_result, write_parent


def export_csv(result, output):
    rows = rows_from_result(result)
    columns = sorted({key for row in rows for key in row}) or ["status"]
    path = write_parent(output)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return {"output": str(path), "rows": len(rows), "format": "csv"}
