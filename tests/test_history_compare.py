import pytest

from recon.history import compare_history, compare_snapshots, save_snapshot


def test_compare_added_and_resolved():
    old = {"differences": [{"key": "A", "status": "mismatch"}, {"key": "B"}]}
    new = {"differences": [{"key": "A", "status": "mismatch"}, {"key": "C"}]}
    result = compare_snapshots(old, new)
    assert result["unchanged"] == 1 and result["added"] == [{"key": "C"}] and result["resolved"] == [{"key": "B"}]


def test_compare_empty_boundary():
    assert compare_snapshots({"differences": []}, {"differences": []}) == {"added": [], "resolved": [], "unchanged": 0}


def test_compare_missing_differences_is_empty():
    assert compare_snapshots({}, {"summary": {"differences": 2}})["added"] == []


def test_compare_history_indices(tmp_path):
    rules = tmp_path / "rules.yaml"
    rules.write_text("left: a.csv\nright: b.csv\n", encoding="utf-8")
    (tmp_path / "a.csv").write_text("id\nA\n", encoding="utf-8")
    (tmp_path / "b.csv").write_text("id\nA\n", encoding="utf-8")
    save_snapshot(rules, {"differences": [{"key": "A"}]}, tmp_path / "h")
    save_snapshot(rules, {"differences": []}, tmp_path / "h")
    assert compare_history(tmp_path / "h", 0, 1)["resolved"] == [{"key": "A"}]


def test_compare_invalid_index(tmp_path):
    with pytest.raises(ValueError):
        compare_history(tmp_path, 0, 1)
