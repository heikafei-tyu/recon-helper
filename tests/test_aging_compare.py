import pytest

from recon.aging import compare_aging


def _bucket(ratio):
    return {"ratio": str(ratio)}


def test_aging_stable():
    assert compare_aging({"360+": _bucket(".2")}, {"360+": _bucket(".2")})["360+"]["assessment"] == "稳定"


def test_aging_deteriorates():
    result = compare_aging({"360+": _bucket(".3")}, {"360+": _bucket(".2")}, ".05")
    assert result["360+"]["assessment"] == "账龄恶化" and result["360+"]["change"] == "0.1"


def test_aging_improves():
    assert compare_aging({"360+": _bucket(".1")}, {"360+": _bucket(".2")}, ".05")["360+"]["assessment"] == "账龄改善"


def test_aging_zero_threshold_boundary():
    assert compare_aging({"0-30": _bucket(".11")}, {"0-30": _bucket(".10")}, "0")["0-30"]["assessment"] == "账龄恶化"


def test_aging_invalid_thresholds():
    with pytest.raises(ValueError):
        compare_aging({}, {}, "bad")
    with pytest.raises(ValueError):
        compare_aging({}, {}, "-0.1")
