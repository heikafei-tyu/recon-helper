from recon.plugins import run_plugin


def test_threshold_plugin():
    assert run_plugin("threshold_check", [1, 10], [1, 1], {"threshold": 2})[0]["index"] == 1

def test_sum_plugin():
    assert run_plugin("custom_sum", [1, 2], [1, 1])[0]["difference"] == 1

def test_date_plugin():
    result = run_plugin("date_range", ["2024-01-01", "2025-01-01"], [], {"start": "2024-01-01", "end": "2024-12-31"})
    assert result[0]["status"] == "date_out_of_range"
