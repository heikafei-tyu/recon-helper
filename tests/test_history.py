import json

from recon.history import list_history, load_history, save_snapshot


def test_snapshot_roundtrip(tmp_path):
    data = tmp_path / "data.csv"
    data.write_text("id\n1\n", encoding="utf-8")
    rules = tmp_path / "rules.json"
    rules.write_text(json.dumps({"left": "data.csv", "right": "data.csv"}), encoding="utf-8")
    path = save_snapshot(rules, {"differences": [], "left_rows": 1, "right_rows": 1}, tmp_path / "history")
    assert (
        path.exists()
        and len(list_history(tmp_path / "history")) == 1
        and load_history(tmp_path / "history")[0]["summary"]["differences"] == 0
    )
