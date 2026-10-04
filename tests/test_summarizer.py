import pytest

from recon.engine.summarizer import summarize


def test_summarize_empty_result_has_stable_metrics():
    result = summarize([], 10, 10)
    assert result["conclusion"] == "通过"
    assert result["status_counts"] == {}
    assert result["severity_counts"] == {}
    assert result["matched_rows"] == 10
    assert result["difference_rate"] == 0.0


def test_summarize_counts_status_severity_and_rate():
    differences = [
        {"status": "mismatch", "severity": "严重"},
        {"status": "left_only", "severity": "致命"},
        {"status": "within_tolerance", "severity": "提示"},
    ]
    result = summarize(differences, 4, 3)
    assert result["status_counts"] == {"mismatch": 1, "left_only": 1, "within_tolerance": 1}
    assert result["severity_counts"] == {"严重": 1, "致命": 1, "提示": 1}
    assert result["matched_rows"] == 3
    assert result["difference_rate"] == pytest.approx(3 / 4)


@pytest.mark.parametrize("left,right", [(-1, 0), (0, -1), (-1, -1)])
def test_summarize_rejects_negative_row_counts(left, right):
    with pytest.raises(ValueError, match="行数不能为负数"):
        summarize([], left, right)


def test_summarize_accepts_generator_and_zero_comparison_base():
    result = summarize(({"status": "mismatch"} for _ in range(2)), 0, 0)
    assert result["difference_count"] == 2
    assert result["matched_rows"] == 0
    assert result["difference_rate"] == 0.0
