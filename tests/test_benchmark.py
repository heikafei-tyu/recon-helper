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
    assert result["bytes"] == path.stat().st_size
    assert result["duplicates"] == 1
    assert result["seconds"] >= 0
    assert result["peak_memory_mb"] >= 0
    assert result["duplicate_check"] is True


def test_benchmark_without_duplicate_check(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("id\n1\n1\n", encoding="utf-8")
    result = benchmark(path, check_duplicates=False)
    assert result["duplicates"] is None
    assert result["duplicate_check"] is False


def test_negative_timeout_rejected(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("id\n1\n", encoding="utf-8")
    import pytest
    with pytest.raises(ValueError, match="不能为负数"):
        benchmark(path, timeout=-1)


def test_progress_output(tmp_path, capsys):
    path = tmp_path / "data.csv"
    path.write_text("id\n" + "\n".join(str(i) for i in range(10000)) + "\n", encoding="utf-8")
    benchmark(path, progress=True)
    assert "processed_rows=10000" in capsys.readouterr().out
