from recon.store import ResultStore


def test_job_lifecycle_persists(tmp_path):
    with ResultStore(tmp_path / "jobs.db") as store:
        store.save_job("daily", "rules.yaml", "23:00", "running")
        store.update_job_run("daily")
        store.update_job_run("daily", "broken")
        job = store.jobs()[0]
    assert job["status"] == "running" and job["run_count"] == 2 and job["failure_count"] == 1
