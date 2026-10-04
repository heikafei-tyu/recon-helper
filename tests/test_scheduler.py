import time

from recon.scheduler import list_jobs, start, stop


def test_scheduler_short_interval(tmp_path):
    (tmp_path / "l.csv").write_text("id,v\na,1\n", encoding="utf-8"); (tmp_path / "r.csv").write_text("id,v\na,1\n", encoding="utf-8")
    rules = tmp_path / "rules.yaml"; rules.write_text("left: l.csv\nright: r.csv\nkey: id\ncolumns: [v]\n", encoding="utf-8")
    name = f"job-{time.time_ns()}"; job = start(name, rules, interval=0.05); time.sleep(0.2); stopped = stop(name)
    assert job["status"] == "running" and stopped["status"] == "stopped" and list_jobs()
