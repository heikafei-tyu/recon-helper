"""Operational orchestration and governance views for reconciliation runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Iterable

from .engine import run_rules
from .store import ResultStore


@dataclass
class BatchItem:
    name: str
    rules: str
    status: str = "pending"
    elapsed: float = 0.0
    differences: int = 0
    error: str | None = None
    history_id: int | None = None


def run_batch(rule_files: Iterable[str | Path], store_path="recon_history.db", stop_on_error=False, name=None):
    """Run a group of rule files and persist every completed result."""
    items: list[BatchItem] = []
    started = perf_counter()
    rule_files = list(rule_files)
    with ResultStore(store_path) as store:
        batch_id = store.create_batch(
            name or f"batch-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}", rule_files
        )
        task_rows = [item["id"] for item in store.batches(1)[0]["tasks"]]
        for raw_path in rule_files:
            path = Path(raw_path)
            item = BatchItem(path.stem, str(path))
            item_started = perf_counter()
            try:
                result = run_rules(path)
                item.status = "passed" if not result.get("differences") else "differences"
                item.differences = len(result.get("differences", []))
                item.history_id = store.save({"rules_file": str(path)}, result)
            except Exception as exc:
                item.status = "failed"
                item.error = f"{type(exc).__name__}: {exc}"
                if stop_on_error:
                    item.elapsed = round(perf_counter() - item_started, 6)
                    store.update_batch_task(task_rows[len(items)], item.status, 1, None, item.elapsed, item.error)
                    items.append(item)
                    break
            item.elapsed = round(perf_counter() - item_started, 6)
            task_id = task_rows[len(items)]
            store.update_batch_task(task_id, item.status, 1, item.history_id, item.elapsed, item.error)
            items.append(item)
    return {
        "batch_id": batch_id,
        "items": [asdict(item) for item in items],
        "total": len(items),
        "elapsed": round(perf_counter() - started, 6),
        "passed": sum(item.status == "passed" for item in items),
        "with_differences": sum(item.status == "differences" for item in items),
        "failed": sum(item.status == "failed" for item in items),
    }


def history_summary(store_path="recon_history.db", limit=100):
    """Return dashboard-ready aggregate metrics and daily difference trend."""
    if limit < 1 or limit > 10000:
        raise ValueError("limit 必须在 1 到 10000 之间")
    with ResultStore(store_path) as store:
        records = store.query(limit=limit)
    trend: dict[str, int] = {}
    for record in records:
        day = record["created_at"][:10]
        trend[day] = trend.get(day, 0) + record["difference_count"]
    return {
        "total_runs": len(records),
        "difference_total": sum(item["difference_count"] for item in records),
        "fatal_runs": sum(item["severity"] == "fatal" for item in records),
        "trend": [{"date": date, "differences": count} for date, count in sorted(trend.items())],
        "recent": records[:10],
    }


def review_queue(store_path="recon_history.db", limit=100):
    """Flatten unreviewed differences for an operations queue."""
    if limit < 1:
        raise ValueError("limit 必须为正数")
    with ResultStore(store_path) as store:
        records = store.query(limit=limit)
    queue = []
    for record in records:
        for difference in record["differences"]:
            if difference.get("review_status", "未处理") == "未处理":
                queue.append(
                    {
                        "history_id": record["id"],
                        "created_at": record["created_at"],
                        "severity": record["severity"],
                        **difference,
                    }
                )
    return {"total": len(queue), "items": queue[:limit]}


def export_history(store_path, output, severity=None):
    """Export a compact JSON history snapshot for audit handoff."""
    with ResultStore(store_path) as store:
        records = store.query(severity=severity, limit=10000)
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    import json

    destination.write_text(
        json.dumps(
            {"exported_at": datetime.now(timezone.utc).isoformat(), "records": records}, ensure_ascii=False, indent=2
        ),
        encoding="utf-8",
    )
    return {"output": str(destination), "records": len(records)}
