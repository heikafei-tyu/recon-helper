import csv
import time
from pathlib import Path


def stream_csv(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        yield from csv.DictReader(stream)


def benchmark(path, key="id"):
    started = time.perf_counter()
    rows = 0
    seen = set()
    duplicates = 0
    for row in stream_csv(path):
        rows += 1
        value = row.get(key)
        if value in seen:
            duplicates += 1
        seen.add(value)
    return {"file": str(path), "rows": rows, "duplicates": duplicates, "seconds": round(time.perf_counter() - started, 6)}
