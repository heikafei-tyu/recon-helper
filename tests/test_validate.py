from recon.cli import main


def test_validate_command(tmp_path, capsys):
    (tmp_path / "left.csv").write_text("id,value\na,1\n", encoding="utf-8")
    (tmp_path / "right.csv").write_text("id,value\na,1\n", encoding="utf-8")
    rules = tmp_path / "rules.yaml"
    rules.write_text("left: left.csv\nright: right.csv\nkey: id\ncolumns: [value]\n", encoding="utf-8")
    assert main(["validate", str(rules)]) == 0
    assert '"valid": true' in capsys.readouterr().out
