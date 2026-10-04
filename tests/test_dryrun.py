import json
import pytest
from recon.cli import main
from recon.dryrun import dry_run


def _fixture(tmp_path):
    (tmp_path / "left.csv").write_text("id,amount\na,10\nb,20\n", encoding="utf-8")
    (tmp_path / "right.csv").write_text("id,amount\na,12\nc,30\n", encoding="utf-8")
    path = tmp_path / "rules.yaml"
    path.write_text("left: left.csv\nright: right.csv\nkey: id\ncolumns: [amount]\n", encoding="utf-8")
    return path


def test_dryrun_exposes_tables_keys_and_steps(tmp_path):
    result = dry_run(_fixture(tmp_path))
    assert result["tables"]["left"]["row_count"] == 2
    assert result["matched_keys"] == ["a"]
    compare = next(item for item in result["steps"] if item["step"] == "compare")
    assert compare["difference"] == "-2"


def test_dryrun_cli_outputs_json(tmp_path, capsys):
    assert main(["dryrun", str(_fixture(tmp_path))]) == 0
    assert json.loads(capsys.readouterr().out)["matched_keys"] == ["a"]


def test_dryrun_rejects_finance_checks(tmp_path):
    path = tmp_path / "checks.yaml"
    path.write_text("checks:\n  - type: total_check\n", encoding="utf-8")
    with pytest.raises(ValueError, match="单条"):
        dry_run(path)
