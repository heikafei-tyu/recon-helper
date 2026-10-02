import pytest

from recon.engine import run_rules


def setup_rule(tmp_path, left, right, rules=None):
    (tmp_path / "left.csv").write_text(left, encoding="utf-8")
    (tmp_path / "right.csv").write_text(right, encoding="utf-8")
    path = tmp_path / "rules.yaml"
    path.write_text(rules or "left: left.csv\nright: right.csv\nkey: id\ncolumns: [amount]\n", encoding="utf-8")
    return path


def test_locates_numeric_difference(tmp_path):
    path = setup_rule(tmp_path, "id,amount\n001,10.00\n", "id,amount\n001,11\n")
    difference = run_rules(path)["differences"][0]
    assert difference["key"] == "001"
    assert difference["left_row"] == difference["right_row"] == 2
    assert difference["column"] == "amount"
    assert difference["difference"] == "-1.00"


def test_equivalent_numbers_and_missing_rows(tmp_path):
    path = setup_rule(tmp_path, "id,amount\na,10.00\nb,2\n", "id,amount\na,10\nc,3\n")
    assert [d["status"] for d in run_rules(path)["differences"]] == ["left_only", "right_only"]


def test_column_tolerance_and_rounding(tmp_path):
    rules = "left: left.csv\nright: right.csv\nkey: id\ncolumns: [amount]\ntolerance:\n  amount:\n    absolute: '0.01'\n    round: 2\n"
    path = setup_rule(tmp_path, "id,amount\na,10.00\nb,10.00\nc,10.00\n", "id,amount\na,10.01\nb,10.02\nc,11.00\n", rules)
    results = run_rules(path)["differences"]
    assert [item["status"] for item in results] == ["within_tolerance", "mismatch", "mismatch"]


@pytest.mark.parametrize("left", ["id,amount\na,1\na,2\n", "id,amount\n,1\n", "id,other\na,1\n"])
def test_invalid_input(tmp_path, left):
    path = setup_rule(tmp_path, left, "id,amount\na,1\n")
    with pytest.raises(ValueError):
        run_rules(path)


@pytest.mark.parametrize("rules", ["[]", "left: left.csv", "left: left.csv\nright: right.csv\nkey: id\ncolumns: [amount, amount]", "left: [x]\nright: right.csv\nkey: id\ncolumns: [amount]"])
def test_invalid_rules(tmp_path, rules):
    path = setup_rule(tmp_path, "id,amount\na,1\n", "id,amount\na,1\n", rules)
    with pytest.raises(ValueError):
        run_rules(path)
