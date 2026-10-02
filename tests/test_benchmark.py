import csv

from recon.benchmark import benchmark, stream_csv


def test_streaming_benchmark(tmp_path):
    path = tmp_path / "large.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["id", "amount"])
        writer.writerows([[str(i), str(i)] for i in range(1000)] + [["1", "duplicate"]])
    assert sum(1 for _ in stream_csv(path)) == 1001
    result = benchmark(path)
    assert result["rows"] == 1001
    assert result["duplicates"] == 1
    assert result["seconds"] >= 0
