"""SQLite-backed incremental fingerprints with legacy JSON migration."""

import json
import sqlite3
from pathlib import Path


class FingerprintStore:
    def __init__(self, path="recon_history.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS fingerprints (path TEXT PRIMARY KEY, digest TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)"
        )
        self.db.commit()

    def get(self, path):
        row = self.db.execute("SELECT digest FROM fingerprints WHERE path=?", (str(path),)).fetchone()
        return row[0] if row else None

    def put_many(self, values):
        self.db.executemany(
            "INSERT INTO fingerprints(path,digest) VALUES(?,?) ON CONFLICT(path) DO UPDATE SET digest=excluded.digest, updated_at=CURRENT_TIMESTAMP",
            [(str(path), digest) for path, digest in values.items()],
        )
        self.db.commit()

    def migrate_json(self, manifest):
        source = Path(manifest)
        if not source.exists():
            return 0
        data = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return 0
        self.put_many(data)
        return len(data)

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
