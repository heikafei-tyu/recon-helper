from openpyxl import load_workbook

from recon.report import create_report


def test_report_and_incremental_skip(tmp_path):
    (tmp_path / "custom-left.csv").write_text("id,amount\na,1\n", encoding="utf-8")
    (tmp_path / "custom-right.csv").write_text("id,amount\na,2\n", encoding="utf-8")
    rules = tmp_path / "rules.yaml"
    rules.write_text("left: custom-left.csv\nright: custom-right.csv\nkey: id\ncolumns: [amount]\n", encoding="utf-8")
    output = tmp_path / "report.xlsx"
    assert create_report(rules, output)["skipped"] is False
    book = load_workbook(output)
    assert book.sheetnames == ["Differences", "Summary"]
    assert book["Differences"].freeze_panes == "A2"
    assert book["Summary"]["A6"].value == "within_tolerance" or book["Summary"]["A6"].value == "left_only"
    assert create_report(rules, output, incremental=True)["skipped"] is True
