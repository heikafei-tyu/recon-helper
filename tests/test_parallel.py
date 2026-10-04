import pytest

from recon.parallel import default_workers, run_rules_parallel


def test_parallel_rules(tmp_path):
    files = []
    for index in range(3):
        left = tmp_path / f"l{index}.csv"
        right = tmp_path / f"r{index}.csv"
        rule = tmp_path / f"r{index}.yaml"
        left.write_text("id,v\na,1\n", encoding="utf-8")
        right.write_text("id,v\na,1\n", encoding="utf-8")
        rule.write_text(f"left: {left.name}\nright: {right.name}\nkey: id\ncolumns: [v]\n", encoding="utf-8")
        files.append(rule)
    assert len(run_rules_parallel(files, 2)) == 3


def test_parallel_invalid_workers():
    with pytest.raises(ValueError):
        run_rules_parallel(["missing.yaml"], 0)


def test_default_workers_positive():
    assert default_workers() >= 1
