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


@pytest.mark.parametrize("tolerance", ["-1", "0.1", "{absolute: -1}", "{round: 9}"])
def test_invalid_tolerance(tmp_path, tolerance):
    rules = f"left: left.csv\nright: right.csv\nkey: id\ncolumns: [amount]\ntolerance:\n  amount: {tolerance}\n"
    path = setup_rule(tmp_path, "id,amount\na,1\n", "id,amount\na,1\n", rules)
    with pytest.raises(ValueError):
        run_rules(path)


def test_tolerance_reason_and_priority(tmp_path):
    rules = "left: left.csv\nright: right.csv\nkey: id\ncolumns: [amount]\ntolerance:\n  amount:\n    absolute: '0.10'\n    relative: '0.0005'\n    priority: 5\n"
    path = setup_rule(tmp_path, "id,amount\na,100.00\n", "id,amount\na,100.05\n", rules)
    item = run_rules(path)["differences"][0]
    assert item["status"] == "within_tolerance"
    assert item["tolerance_type"] == "absolute"
    assert item["rule_priority"] == 5


def test_priority_selects_named_tolerance_rule(tmp_path):
    rules = "left: left.csv\nright: right.csv\nkey: id\ncolumns: [amount]\ntolerance:\n  amount:\n    - name: strict\n      absolute: '0.01'\n      priority: 1\n    - name: cents\n      absolute: '0.10'\n      priority: 10\n"
    path = setup_rule(tmp_path, "id,amount\na,10.00\n", "id,amount\na,10.05\n", rules)
    item = run_rules(path)["differences"][0]
    assert item["tolerance_rule"] == "cents"
    assert item["rule_priority"] == 10


def test_lower_priority_rule_can_match(tmp_path):
    rules = "left: left.csv\nright: right.csv\nkey: id\ncolumns: [amount]\ntolerance:\n  amount:\n    - name: strict\n      absolute: '0.01'\n      priority: 20\n    - name: business\n      absolute: '0.10'\n      priority: 10\n"
    path = setup_rule(tmp_path, "id,amount\na,10.00\n", "id,amount\na,10.05\n", rules)
    item = run_rules(path)["differences"][0]
    assert item["tolerance_rule"] == "business"
    assert item["rule_priority"] == 10


def test_priority_audit_and_raw_rounding(tmp_path):
    rules = "left: left.csv\nright: right.csv\nkey: id\ncolumns: [amount]\ntolerance:\n  amount:\n    - name: strict\n      absolute: '0.01'\n      priority: 20\n    - name: business\n      absolute: '0.10'\n      priority: 10\n      rounding:\n        mode: raw\n"
    path = setup_rule(tmp_path, 'id,amount\na,"1,234.56"\n', "id,amount\na,1234.60\n", rules)
    item = run_rules(path)["differences"][0]
    assert item["tolerance_rule"] == "business"
    assert item["rounding_mode"] == "raw"
    assert item["ignored_rules"] == ["strict"]


def test_text_normalization_and_null_policy(tmp_path):
    rules = "left: left.csv\nright: right.csv\nkey: id\ncolumns: [name, amount]\nnormalize:\n  trim: true\n  casefold: true\nnull_policy: equal\n"
    path = setup_rule(tmp_path, "id,name,amount\n A , Zhang San,\n", "id,name,amount\na, zhang san,\n", rules)
    assert run_rules(path)["differences"] == []


def test_key_mapping_between_tables(tmp_path):
    rules = "left: left.csv\nright: right.csv\nkeys: [customer, date]\nkey_mapping:\n  left: [customer, date]\n  right: [client, trade_date]\ncolumns:\n  - left: amount\n    right: total\n"
    path = setup_rule(tmp_path, "customer,date,amount\na,2026-01-01,10\n", "client,trade_date,total\na,2026-01-01,10\n", rules)
    assert run_rules(path)["differences"] == []


def test_rule_filters_and_field_transforms(tmp_path):
    rules = "left: left.csv\nright: right.csv\nkey: id\ncolumns: [amount]\nfilters:\n  left:\n    - field: status\n      op: eq\n      value: keep\ntransforms:\n  amount: [trim, decimal]\n"
    path = setup_rule(tmp_path, "id,amount,status\na, 10.00 ,keep\nb,9,skip\n", "id,amount\na,10\nb,9\n", rules)
    assert [item["status"] for item in run_rules(path)["differences"]] == ["right_only"]


def test_composite_key_and_field_mapping(tmp_path):
    rules = "left: left.csv\nright: right.csv\nkeys: [customer, date]\ncolumns:\n  - left: amount\n    right: total\n"
    path = setup_rule(tmp_path, "customer,date,amount\na,2026-01-01,10\n", "customer,date,total\na,2026-01-01,12\n", rules)
    item = run_rules(path)["differences"][0]
    assert item["key"] == ["a", "2026-01-01"] or item["key"] == ("a", "2026-01-01")
    assert item["left_value"] == "10"
    assert item["right_value"] == "12"


@pytest.mark.parametrize("rules", ["[]", "left: left.csv", "left: left.csv\nright: right.csv\nkey: id\ncolumns: [amount, amount]", "left: [x]\nright: right.csv\nkey: id\ncolumns: [amount]"])
def test_invalid_rules(tmp_path, rules):
    path = setup_rule(tmp_path, "id,amount\na,1\n", "id,amount\na,1\n", rules)
    with pytest.raises(ValueError):
        run_rules(path)
