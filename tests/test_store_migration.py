import json

from recon.store import ResultStore


def test_json_snapshot_migration(tmp_path):
    history = tmp_path / "history"; history.mkdir()
    (history / "one.json").write_text(json.dumps({"rules": {"left": "a"}, "files": {"a": "x"}, "differences": []}), encoding="utf-8")
    with ResultStore(tmp_path / "db.sqlite") as store:
        assert store.migrate_json(history) == 1
        assert store.query()[0]["difference_count"] == 0
