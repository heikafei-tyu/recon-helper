import json

from .common import rows_from_result, write_parent


def export_json(result, output):
    path = write_parent(output)
    path.write_text(json.dumps(rows_from_result(result), ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return {"output": str(path), "rows": len(rows_from_result(result)), "format": "json"}
