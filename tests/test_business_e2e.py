from recon.engine import run_rules


def case(tmp_path, left, right, name):
    (tmp_path / "left.csv").write_text(left, encoding="utf-8")
    (tmp_path / "right.csv").write_text(right, encoding="utf-8")
    rules = tmp_path / f"{name}.yaml"
    rules.write_text("left: left.csv\nright: right.csv\nkey: id\ncolumns: [amount]\n", encoding="utf-8")
    return run_rules(rules)


def test_monthly_salary_reconciliation(tmp_path):
    result = case(tmp_path, "id,amount\nemp-1,10000\n", "id,amount\nemp-1,10000\n", "salary")
    assert result["differences"] == []


def test_quarter_summary_difference(tmp_path):
    result = case(tmp_path, "id,amount\nq1,300\n", "id,amount\nq1,301\n", "quarter")
    assert result["differences"][0]["difference"] == "-1"


def test_cross_year_link(tmp_path):
    result = case(tmp_path, "id,amount\n2024,100\n", "id,amount\n2024,100\n", "year")
    assert result["differences"] == []
