import pytest

from recon.finance_checks import run_finance_checks


def write(path, text):
    path.write_text(text, encoding="utf-8")


def total_rule():
    return {"type": "total_check", "detail": "detail.csv", "summary": "summary.csv", "columns": ["amount"]}


def test_total_check_normal_and_one_yuan_difference(tmp_path):
    write(tmp_path / "detail.csv", "amount\n10\n20\n")
    write(tmp_path / "summary.csv", "amount\n30\n")
    assert run_finance_checks(tmp_path, [total_rule()]) == []
    write(tmp_path / "summary.csv", "amount\n31\n")
    result = run_finance_checks(tmp_path, [total_rule()])
    assert result[0]["status"] == "total_mismatch"
    assert result[0]["difference"] == "-1"


@pytest.mark.parametrize("rule", [{"type": "total_check"}, {"type": "total_check", "detail": "x", "summary": "y", "columns": []}, {"type": "unknown"}])
def test_total_check_rejects_invalid_rules(tmp_path, rule):
    with pytest.raises(ValueError):
        run_finance_checks(tmp_path, [rule])


def test_chain_check_supports_three_tables_and_detects_mismatch(tmp_path):
    write(tmp_path / "a.csv", "期初,期末\n0,100\n")
    write(tmp_path / "b.csv", "期初,期末\n100,200\n")
    write(tmp_path / "c.csv", "期初,期末\n199,300\n")
    rule = {"type": "chain_check", "tables": ["a.csv", "b.csv", "c.csv"]}
    result = run_finance_checks(tmp_path, [rule])
    assert len(result) == 1 and result[0]["difference"] == "1"
    write(tmp_path / "c.csv", "期初,期末\n200,300\n")
    assert run_finance_checks(tmp_path, [rule]) == []


@pytest.mark.parametrize("rule", [{"type": "chain_check", "tables": ["a.csv"]}, {"type": "chain_check", "tables": "a.csv"}, {"type": "chain_check", "tables": ["a.csv", "missing.csv"]}])
def test_chain_check_rejects_invalid_rules(tmp_path, rule):
    write(tmp_path / "a.csv", "期初,期末\n1,2\n")
    write(tmp_path / "b.csv", "期初,期末\n2,3\n")
    with pytest.raises(ValueError):
        run_finance_checks(tmp_path, [rule])


def test_missing_check_detects_missing_month_and_day(tmp_path):
    write(tmp_path / "monthly.csv", "month,amount\n2026-01,1\n2026-03,1\n")
    rule = {"type": "missing_check", "file": "monthly.csv", "time_column": "month", "frequency": "month", "start": "2026-01", "end": "2026-03"}
    assert run_finance_checks(tmp_path, [rule])[0]["missing"] == "2026-02"
    write(tmp_path / "daily.csv", "day,amount\n2026-01-01,1\n2026-01-03,1\n")
    day_rule = {"type": "missing_check", "file": "daily.csv", "time_column": "day", "frequency": "day"}
    assert run_finance_checks(tmp_path, [day_rule])[0]["missing"] == "2026-01-02"


@pytest.mark.parametrize("rule", [{"type": "missing_check", "file": "x", "time_column": "day", "frequency": "year"}, {"type": "missing_check", "file": "x", "time_column": "day", "frequency": "day", "start": "bad"}, {"type": "missing_check", "file": "x", "time_column": "day", "frequency": "day", "start": "2026-02-01", "end": "2026-01-01"}])
def test_missing_check_rejects_invalid_rules(tmp_path, rule):
    write(tmp_path / "x", "day\n2026-01-01\n")
    with pytest.raises(ValueError):
        run_finance_checks(tmp_path, [rule])
