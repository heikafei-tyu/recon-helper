from recon.cli import main


def test_html_report(tmp_path):
    (tmp_path / "left.csv").write_text("id,value\na,1\n", encoding="utf-8")
    (tmp_path / "right.csv").write_text("id,value\na,2\n", encoding="utf-8")
    rules = tmp_path / "rules.yaml"
    rules.write_text("left: left.csv\nright: right.csv\nkey: id\ncolumns: [value]\n", encoding="utf-8")
    output = tmp_path / "report.html"
    assert main(["report", str(rules), "--html", str(output)]) == 0
    assert "mismatch" in output.read_text(encoding="utf-8")
