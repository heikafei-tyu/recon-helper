import json

from recon.cli import main


def test_benchmark_json_output(tmp_path):
    source = tmp_path / "data.csv"
    source.write_text("id\n1\n2\n", encoding="utf-8")
    target = tmp_path / "results" / "bench.json"
    assert main(["bench", str(source), "--json-out", str(target)]) == 0
    result = json.loads(target.read_text(encoding="utf-8"))
    assert result["rows"] == 2
