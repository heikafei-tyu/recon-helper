from recon.fingerprint_store import FingerprintStore


def test_store_and_migrate(tmp_path):
    manifest = tmp_path / "legacy.json"; manifest.write_text('{"a.csv":"abc"}', encoding="utf-8")
    with FingerprintStore(tmp_path / "recon_history.db") as store:
        assert store.migrate_json(manifest) == 1
        assert store.get("a.csv") == "abc"
        store.put_many({"b.csv": "def"})
        assert store.get("b.csv") == "def"


def test_missing_legacy(tmp_path):
    with FingerprintStore(tmp_path / "x.db") as store:
        assert store.migrate_json(tmp_path / "none.json") == 0
