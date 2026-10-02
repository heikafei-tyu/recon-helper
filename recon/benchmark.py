import csv
import time
import tracemalloc
from pathlib import Path


def stream_csv(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        yield from csv.DictReader(stream)


def benchmark(path, key="id", check_duplicates=True, timeout=None):
    started = time.perf_counter()
    tracemalloc.start()
    rows = 0
    seen = set()
    duplicates = 0
    for row in stream_csv(path):
        rows += 1
        value = row.get(key)
        if check_duplicates and value in seen:
            duplicates += 1
        if check_duplicates:
            seen.add(value)
        if timeout is not None and time.perf_counter() - started > timeout:
            tracemalloc.stop()
            raise TimeoutError(f"超过 {timeout} 秒")
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"file": str(path), "rows": rows, "duplicates": duplicates if check_duplicates else None, "seconds": round(time.perf_counter() - started, 6), "peak_memory_mb": round(peak / 1024 / 1024, 3), "duplicate_check": check_duplicates}
