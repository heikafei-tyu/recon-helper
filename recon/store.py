"""SQLite persistence for reconciliation results and searchable differences."""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class ResultStore:
    def __init__(self, path="recon_history.db"):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, timeout=30, check_same_thread=False)
        self.db.execute("PRAGMA busy_timeout=30000")
        try:
            self.db.execute("PRAGMA journal_mode=WAL")
        except sqlite3.OperationalError:
            # Another initializer may hold the schema lock; normal writes still use the busy timeout.
            pass
        self.db.executescript("CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, rules TEXT NOT NULL, fingerprints TEXT NOT NULL, severity TEXT NOT NULL, difference_count INTEGER NOT NULL); CREATE TABLE IF NOT EXISTS diffs (id INTEGER PRIMARY KEY, result_id INTEGER NOT NULL REFERENCES results(id) ON DELETE CASCADE, table_name TEXT, severity TEXT, payload TEXT NOT NULL); CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, actor TEXT NOT NULL, method TEXT NOT NULL, path TEXT NOT NULL, status INTEGER NOT NULL)")
        self.db.commit()

    def save(self, rules, result, fingerprints=None):
        differences = result.get("differences", [])
        severity = "fatal" if any(item.get("status") in {"left_only", "right_only", "data_missing"} for item in differences) else "serious" if differences else "pass"
        cursor = self.db.execute("INSERT INTO results(created_at,rules,fingerprints,severity,difference_count) VALUES(?,?,?,?,?)", (datetime.now(timezone.utc).isoformat(), json.dumps(rules, ensure_ascii=False), json.dumps(fingerprints or {}, ensure_ascii=False), severity, len(differences)))
        result_id = cursor.lastrowid
        self.db.executemany("INSERT INTO diffs(result_id,table_name,severity,payload) VALUES(?,?,?,?)", [(result_id, item.get("left_table") or item.get("from"), "fatal" if item.get("status") in {"left_only", "right_only", "data_missing"} else "serious", json.dumps(item, ensure_ascii=False)) for item in differences])
        self.db.commit(); return result_id

    def query(self, table_name=None, severity=None, limit=100):
        sql = "SELECT id,created_at,rules,fingerprints,severity,difference_count FROM results WHERE 1=1"; args = []
        if severity: sql += " AND severity=?"; args.append(severity)
        if table_name: sql += " AND id IN (SELECT result_id FROM diffs WHERE table_name=?)"; args.append(table_name)
        sql += " ORDER BY id DESC LIMIT ?"; args.append(limit)
        rows = []
        for row in self.db.execute(sql, args):
            rows.append({"id": row[0], "created_at": row[1], "rules": json.loads(row[2]), "files": json.loads(row[3]), "severity": row[4], "difference_count": row[5], "differences": [json.loads(item[0]) for item in self.db.execute("SELECT payload FROM diffs WHERE result_id=?", (row[0],))]})
        return rows

    def migrate_json(self, directory="history"):
        count = 0
        for path in sorted(Path(directory).glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.save(data.get("rules", {}), {"differences": data.get("differences", [])}, data.get("files", {})); count += 1
        return count

    def audit(self, actor, method, path, status):
        self.db.execute("INSERT INTO audit_log(created_at,actor,method,path,status) VALUES(?,?,?,?,?)", (datetime.now(timezone.utc).isoformat(), actor, method, path, status)); self.db.commit()

    def audits(self, limit=100):
        return [{"created_at": row[0], "actor": row[1], "method": row[2], "path": row[3], "status": row[4]} for row in self.db.execute("SELECT created_at,actor,method,path,status FROM audit_log ORDER BY id DESC LIMIT ?", (limit,))]

    def close(self): self.db.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()
