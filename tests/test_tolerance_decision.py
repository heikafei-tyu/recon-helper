import pytest

from recon.engine.tolerance import decide


def test_decide_absolute_and_audit_fields():
    result = decide("100.00", "100.05", [{"name": "cents", "absolute": "0.10", "priority": 3}])
    assert result["matched"] is True
    assert result["tolerance_rule"] == "cents"
    assert result["tolerance_type"] == "absolute"


def test_decide_relative_and_raw_rounding():
    result = decide(100, 101, [{"relative": "0.02", "rounding": {"mode": "raw"}}])
    assert result["matched"] is True
    assert result["rounding_mode"] == "raw"


def test_decide_tier_boundary_and_rounding():
    result = decide("10000.004", "10000", [{"tiers": [{"name": "small", "up_to": 10000, "absolute": 1}, {"name": "large", "absolute": 100}], "rounding": {"mode": "cents", "digits": 2}}])
    assert result["matched"] is True
    assert result["tolerance_band"] == "large"


def test_decide_priority_reports_ignored_rule():
    result = decide(10, 10.05, [{"name": "strict", "absolute": 0.01, "priority": 20}, {"name": "business", "absolute": 0.1, "priority": 10}])
    assert result["tolerance_rule"] == "business"
    assert result["ignored_rules"] == ["strict"]


@pytest.mark.parametrize("left,right", [("nan", 1), ("inf", 1)])
def test_decide_rejects_non_finite(left, right):
    with pytest.raises(ValueError, match="有限"):
        decide(left, right)


def test_decide_rejects_negative_tolerance_and_bad_mode():
    with pytest.raises(ValueError, match="非负"):
        decide(1, 2, [{"absolute": -1}])
    with pytest.raises(ValueError, match="舍入模式"):
        decide(1, 2, [{"rounding": {"mode": "bankers"}}])
