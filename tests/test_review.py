from recon.store import ResultStore


def test_review_update_and_query(tmp_path):
    path = tmp_path / "history.db"
    with ResultStore(path) as store:
        history_id = store.save({"name": "rules"}, {"differences": [{"status": "mismatch", "column": "amount"}, {"status": "left_only"}]})
        changed = store.review(history_id, "已修复", "已补录流水")
        assert changed["updated"] == 2
        items = store.query()
        assert {item["review_status"] for item in items[0]["differences"]} == {"已修复"}
        assert items[0]["differences"][0]["review_note"] == "已补录流水"


def test_review_can_update_selected_diff(tmp_path):
    with ResultStore(tmp_path / "history.db") as store:
        history_id = store.save({}, {"differences": [{"status": "mismatch"}, {"status": "mismatch"}]})
        diff_id = store.query()[0]["differences"][0]["diff_id"]
        assert store.review(history_id, "已确认无误", "误差在合同范围", [diff_id])["updated"] == 1
        states = [item["review_status"] for item in store.query()[0]["differences"]]
        assert states == ["已确认无误", "未处理"]


def test_review_rejects_invalid_status(tmp_path):
    with ResultStore(tmp_path / "history.db") as store:
        history_id = store.save({}, {"differences": [{"status": "mismatch"}]})
        try:
            store.review(history_id, "done")
        except ValueError as exc:
            assert "复核状态" in str(exc)
        else:
            raise AssertionError("invalid status accepted")
