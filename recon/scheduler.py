"""Small in-process polling scheduler for recurring reconciliation jobs."""
import threading
import time
from datetime import datetime, timedelta

from .engine import run_rules
from .store import ResultStore

_jobs = {}
_lock = threading.Lock()


def _next_at(hhmm):
    hour, minute = (int(item) for item in hhmm.split(":", 1))
    now = datetime.now(); target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return target if target > now else target + timedelta(days=1)


def start(name, rules_file, at="00:00", interval=None):
    if name in _jobs: raise ValueError(f"任务已存在：{name}")
    with ResultStore() as store: store.save_job(name, rules_file, at if interval is None else f"interval:{interval}", "running")
    stop_event = threading.Event(); job = {"name": name, "rules": str(rules_file), "at": at, "next_run": _next_at(at).isoformat(), "last_result": None, "status": "running", "stop": stop_event}
    def worker():
        while not stop_event.is_set():
            wait = max(0.05, ((_next_at(at) - datetime.now()).total_seconds() if interval is None else float(interval)))
            if stop_event.wait(wait): break
            started_at = datetime.now().isoformat()
            started = time.perf_counter()
            try:
                result = run_rules(rules_file)
                difference_count = len(result.get("differences", []))
                with ResultStore() as store: store.save({"rules": str(rules_file)}, result)
                with ResultStore() as store:
                    store.update_job_run(name)
                    store.save_scheduler_run(name, rules_file, "differences" if difference_count else "passed", difference_count, time.perf_counter() - started, started_at=started_at)
                job["last_result"] = {"differences": difference_count, "at": datetime.now().isoformat()}
            except Exception as exc:
                job["last_result"] = {"error": str(exc), "at": datetime.now().isoformat()}
                with ResultStore() as store:
                    store.update_job_run(name, str(exc))
                    store.save_scheduler_run(name, rules_file, "failed", elapsed=time.perf_counter() - started, error=str(exc), started_at=started_at)
            job["next_run"] = (_next_at(at) if interval is None else datetime.now() + timedelta(seconds=float(interval))).isoformat()
    thread = threading.Thread(target=worker, name=f"recon-schedule-{name}", daemon=True); job["thread"] = thread
    with _lock: _jobs[name] = job
    thread.start(); return public_job(job)


def stop(name):
    with _lock: job = _jobs.get(name)
    if not job: raise ValueError(f"任务不存在：{name}")
    job["stop"].set(); job["status"] = "stopped"
    with ResultStore() as store: store.save_job(name, job["rules"], job["at"], "stopped")
    return public_job(job)


def list_jobs():
    with _lock: active = [public_job(job) for job in _jobs.values()]
    with ResultStore() as store:
        persisted = {item["name"]: item for item in store.jobs()}
    for item in active: persisted[item["name"]].update(item)
    return list(persisted.values())


def public_job(job):
    return {key: value for key, value in job.items() if key not in {"stop", "thread"}}


def run_logs(limit=100):
    """Return recent scheduler execution logs for the CLI and API."""
    with ResultStore() as store:
        return {"runs": store.scheduler_runs(limit)}
