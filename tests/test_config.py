from recon.config import load_config


def test_config_defaults(tmp_path):
    result = load_config(tmp_path)
    assert result["report_template"] == "detailed" and result["config_file"] is None


def test_config_file(tmp_path):
    (tmp_path / ".reconrc").write_text("default_tolerance: '0.01'\nparallel_workers: 4\noutput_dir: reports\nreport_template: simple\n", encoding="utf-8")
    result = load_config(tmp_path)
    assert result["default_tolerance"] == "0.01" and result["parallel_workers"] == 4 and result["report_template"] == "simple"
