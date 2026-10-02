from recon.cli import main


def test_command_error_codes(tmp_path, capsys):
    assert main(["run", str(tmp_path / "missing.yaml")]) == 2
    assert capsys.readouterr().err.startswith("RECON_RULE_ERROR:")
    assert main(["report", str(tmp_path / "missing.yaml")]) == 2
    assert capsys.readouterr().err.startswith("RECON_REPORT_ERROR:")
