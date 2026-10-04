import json
from pathlib import Path
import pytest
from recon.operations import export_history, history_summary, review_queue, run_batch
from recon.store import ResultStore


def _rules(root, name, value="1"):
    (root / f"{name}-l.csv").write_text(f"id,value\na,{value}\n", encoding="utf-8")
    (root / f"{name}-r.csv").write_text(f"id,value\na,{value}\n", encoding="utf-8")
    path = root / f"{name}.yaml"
    path.write_text(f"left: {name}-l.csv\nright: {name}-r.csv\nkey: id\ncolumns: [value]\n", encoding="utf-8")
    return path


def test_run_batch_persists_each_result(tmp_path):
    first, second = _rules(tmp_path, "first"), _rules(tmp_path, "second")
    result = run_batch([first, second], tmp_path / "history.db")
    assert result["total"] == 2 and result["passed"] == 2 and result["batch_id"]
    assert all(item["history_id"] for item in result["items"])


def test_run_batch_reports_failure_and_can_stop(tmp_path):
    good = _rules(tmp_path, "good")
    result = run_batch([tmp_path / "missing.yaml", good], tmp_path / "history.db", stop_on_error=True)
    assert result["failed"] == 1 and result["total"] == 1


def test_history_summary_and_review_queue(tmp_path):
    with ResultStore(tmp_path / "history.db") as store:
        history_id = store.save({}, {"differences": [{"status": "mismatch", "column": "amount"}]})
    summary = history_summary(tmp_path / "history.db")
    queue = review_queue(tmp_path / "history.db")
    assert summary["total_runs"] == 1 and summary["difference_total"] == 1
    assert queue["total"] == 1 and queue["items"][0]["history_id"] == history_id


def test_batch_is_queryable(tmp_path):
    rule = _rules(tmp_path, "tracked")
    result = run_batch([rule], tmp_path / "history.db", name="nightly")
    with ResultStore(tmp_path / "history.db") as store:
        batch = store.batches()[0]
    assert batch["id"] == result["batch_id"] and batch["status"] == "completed"


def test_export_history(tmp_path):
    with ResultStore(tmp_path / "history.db") as store:
        store.save({}, {"differences": []})
    output = tmp_path / "exports" / "history.json"
    result = export_history(tmp_path / "history.db", output)
    assert result["records"] == 1 and json.loads(output.read_text(encoding="utf-8"))["records"]


@pytest.mark.parametrize("limit", [0, -1, 10001])
def test_history_summary_rejects_bad_limit(tmp_path, limit):
    with pytest.raises(ValueError): history_summary(tmp_path / "history.db", limit)
