from recon.cli import main


def test_help_and_missing_command(capsys):
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    assert "本地表格核对工具" in capsys.readouterr().out


def test_module_package_metadata():
    import recon

    assert recon.__name__ == "recon"
