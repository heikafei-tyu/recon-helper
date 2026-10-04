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
        self.db.executescript("CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, rules TEXT NOT NULL, fingerprints TEXT NOT NULL, severity TEXT NOT NULL, difference_count INTEGER NOT NULL); CREATE TABLE IF NOT EXISTS diffs (id INTEGER PRIMARY KEY, result_id INTEGER NOT NULL REFERENCES results(id) ON DELETE CASCADE, table_name TEXT, severity TEXT, payload TEXT NOT NULL, review_status TEXT NOT NULL DEFAULT '未处理', review_note TEXT NOT NULL DEFAULT ''); CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, actor TEXT NOT NULL, method TEXT NOT NULL, path TEXT NOT NULL, status INTEGER NOT NULL); CREATE TABLE IF NOT EXISTS jobs (name TEXT PRIMARY KEY, rules_file TEXT NOT NULL, schedule TEXT NOT NULL, status TEXT NOT NULL, run_count INTEGER NOT NULL DEFAULT 0, failure_count INTEGER NOT NULL DEFAULT 0, last_run TEXT, last_error TEXT); CREATE TABLE IF NOT EXISTS batches (id INTEGER PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL, status TEXT NOT NULL, task_count INTEGER NOT NULL, completed_count INTEGER NOT NULL DEFAULT 0); CREATE TABLE IF NOT EXISTS batch_tasks (id INTEGER PRIMARY KEY, batch_id INTEGER NOT NULL REFERENCES batches(id) ON DELETE CASCADE, name TEXT NOT NULL, rules_file TEXT NOT NULL, status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0, result_id INTEGER, elapsed REAL NOT NULL DEFAULT 0, error TEXT)")
        columns = {row[1] for row in self.db.execute("PRAGMA table_info(diffs)")}
        if "review_status" not in columns:
            self.db.execute("ALTER TABLE diffs ADD COLUMN review_status TEXT NOT NULL DEFAULT '未处理'")
        if "review_note" not in columns:
            self.db.execute("ALTER TABLE diffs ADD COLUMN review_note TEXT NOT NULL DEFAULT ''")
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
            differences = []
            for item in self.db.execute("SELECT payload,review_status,review_note,id FROM diffs WHERE result_id=?", (row[0],)):
                difference = json.loads(item[0]); difference.update({"review_status": item[1], "review_note": item[2], "diff_id": item[3]}); differences.append(difference)
            rows.append({"id": row[0], "created_at": row[1], "rules": json.loads(row[2]), "files": json.loads(row[3]), "severity": row[4], "difference_count": row[5], "differences": differences})
        return rows

    def review(self, result_id, status, note="", diff_ids=None):
        allowed = {"未处理", "已确认无误", "已修复"}
        if status not in allowed:
            raise ValueError("复核状态必须是：未处理、已确认无误、已修复")
        if diff_ids:
            placeholders = ",".join("?" for _ in diff_ids)
            args = [status, note, result_id, *diff_ids]
            cursor = self.db.execute(f"UPDATE diffs SET review_status=?,review_note=? WHERE result_id=? AND id IN ({placeholders})", args)
        else:
            cursor = self.db.execute("UPDATE diffs SET review_status=?,review_note=? WHERE result_id=?", (status, note, result_id))
        self.db.commit()
        return {"history_id": result_id, "updated": cursor.rowcount, "status": status, "note": note}

    def create_batch(self, name, rules_files):
        now = datetime.now(timezone.utc).isoformat()
        cursor = self.db.execute("INSERT INTO batches(name,created_at,status,task_count) VALUES(?,?,?,?)", (name, now, "pending", len(rules_files)))
        batch_id = cursor.lastrowid
        self.db.executemany("INSERT INTO batch_tasks(batch_id,name,rules_file,status) VALUES(?,?,?,?)", [(batch_id, Path(path).stem, str(path), "pending") for path in rules_files])
        self.db.commit(); return batch_id

    def update_batch_task(self, task_id, status, attempts=1, result_id=None, elapsed=0, error=None):
        self.db.execute("UPDATE batch_tasks SET status=?,attempts=?,result_id=?,elapsed=?,error=? WHERE id=?", (status, attempts, result_id, elapsed, error, task_id))
        batch_id = self.db.execute("SELECT batch_id FROM batch_tasks WHERE id=?", (task_id,)).fetchone()[0]
        counts = self.db.execute("SELECT COUNT(*),SUM(status IN ('passed','differences','failed')) FROM batch_tasks WHERE batch_id=?", (batch_id,)).fetchone()
        total, completed = counts[0], counts[1] or 0
        status = "completed" if completed == total else "running"
        self.db.execute("UPDATE batches SET status=?,completed_count=? WHERE id=?", (status, completed, batch_id)); self.db.commit()

    def batches(self, limit=100):
        output = []
        for row in self.db.execute("SELECT id,name,created_at,status,task_count,completed_count FROM batches ORDER BY id DESC LIMIT ?", (limit,)):
            tasks = [{"id": item[0], "name": item[1], "rules_file": item[2], "status": item[3], "attempts": item[4], "result_id": item[5], "elapsed": item[6], "error": item[7]} for item in self.db.execute("SELECT id,name,rules_file,status,attempts,result_id,elapsed,error FROM batch_tasks WHERE batch_id=? ORDER BY id", (row[0],))]
            output.append({"id": row[0], "name": row[1], "created_at": row[2], "status": row[3], "task_count": row[4], "completed_count": row[5], "tasks": tasks})
        return output

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

    def save_job(self, name, rules_file, schedule, status="stopped"):
        self.db.execute("INSERT INTO jobs(name,rules_file,schedule,status) VALUES(?,?,?,?) ON CONFLICT(name) DO UPDATE SET rules_file=excluded.rules_file,schedule=excluded.schedule,status=excluded.status", (name, str(rules_file), schedule, status)); self.db.commit()

    def update_job_run(self, name, error=None):
        self.db.execute("UPDATE jobs SET run_count=run_count+1,last_run=CURRENT_TIMESTAMP,last_error=?,failure_count=failure_count+? WHERE name=?", (error, 1 if error else 0, name)); self.db.commit()

    def jobs(self):
        return [{"name": row[0], "rules": row[1], "schedule": row[2], "status": row[3], "run_count": row[4], "failure_count": row[5], "last_run": row[6], "last_error": row[7]} for row in self.db.execute("SELECT name,rules_file,schedule,status,run_count,failure_count,last_run,last_error FROM jobs ORDER BY name")]

    def close(self): self.db.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()
