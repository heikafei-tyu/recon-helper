"""Parallel execution of independent rule files."""
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .engine import run_rules


def default_workers():
    return max(1, (os.cpu_count() or 2) // 2)


def run_rules_parallel(rule_files, max_workers=None):
    files = [Path(item) for item in rule_files]
    if not files:
        return []
    workers = default_workers() if max_workers is None else max_workers
    if workers < 1:
        raise ValueError("线程数必须为正数")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(run_rules, files))


def benchmark_parallel(rule_files, max_workers=None):
    files = [Path(item) for item in rule_files]
    start = time.perf_counter(); serial = [run_rules(item) for item in files]
    serial_seconds = time.perf_counter() - start
    start = time.perf_counter(); parallel = run_rules_parallel(files, max_workers)
    parallel_seconds = time.perf_counter() - start
    return {"rules": [str(item) for item in files], "serial_seconds": round(serial_seconds, 6), "parallel_seconds": round(parallel_seconds, 6), "workers": max_workers or default_workers(), "serial_results": serial, "parallel_results": parallel}
