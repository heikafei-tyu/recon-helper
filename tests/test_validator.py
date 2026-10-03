import pytest
import yaml

from recon.rules.validator import validate_rules


def write_rule(tmp_path, **changes):
    data = {"left": "left.csv", "right": "right.csv", "key": "id", "columns": ["amount"], **changes}
    (tmp_path / "left.csv").write_text("id,amount\na,1\n", encoding="utf-8")
    (tmp_path / "right.csv").write_text("id,amount\na,1\n", encoding="utf-8")
    path = tmp_path / "rules.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


@pytest.mark.parametrize("changes,fragment", [({}, None), ({"left": ""}, "left"), ({"columns": "amount"}, "columns"), ({"key": 2}, "key"), ({"keys": ["id", "id"]}, "重复"), ({"left_sheet": ""}, "left_sheet"), ({"columns": [1]}, "columns[0]"), ({"tolerance": []}, "tolerance"), ({"tolerance": {"amount": {"absolute": -1}}}, "不能为负"), ({"tolerance": {"amount": {"relative": "x"}}}, "必须是数字"), ({"tolerance": {"amount": {"priority": -1}}}, "priority"), ({"tolerance": {"amount": {"rounding": {"mode": "bad"}}}}, "rounding"), ({"tolerance": {"amount": {"rounding": {"digits": -1}}}}, "digits"), ({"filters": []}, "filters"), ({"transforms": []}, "transforms"), ({"checks": {"type": "x"}}, "checks"), ({"checks": [{"type": "bad"}]}, "未知"), ({"checks": [{"type": "chain_check", "tables": ["a", "a"]}]}, "循环")])
def test_validator_errors(tmp_path, changes, fragment):
    path = write_rule(tmp_path, **changes)
    errors = validate_rules(path)
    if fragment:
        assert any(fragment in error for error in errors)
    else:
        assert errors == []


def test_validator_reports_missing_keys(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("{}", encoding="utf-8")
    errors = validate_rules(path)
    assert len(errors) >= 3
