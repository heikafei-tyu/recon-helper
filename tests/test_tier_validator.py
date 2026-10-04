import pytest

from recon.rules import validate_rules


def _write(tmp_path, tiers):
    (tmp_path / "l.csv").write_text("id,v\na,1\n", encoding="utf-8")
    (tmp_path / "r.csv").write_text("id,v\na,1\n", encoding="utf-8")
    path = tmp_path / "rules.yaml"
    import yaml

    path.write_text(
        yaml.safe_dump(
            {"left": "l.csv", "right": "r.csv", "key": "id", "columns": ["v"], "tolerance": {"v": {"tiers": tiers}}}
        ),
        encoding="utf-8",
    )
    return path


def test_valid_tiers_pass(tmp_path):
    assert validate_rules(_write(tmp_path, [{"up_to": 10000, "absolute": 1}, {"absolute": 100}])) == []


@pytest.mark.parametrize(
    "tiers,fragment",
    [
        ([{"up_to": 100, "absolute": 1}, {"up_to": 50, "absolute": 2}, {"absolute": 3}], "倒挂"),
        ([{"up_to": 100, "absolute": 1}], "缺口"),
        ([{"up_to": 100, "absolute": 1}, {"up_to": 100, "absolute": 2}, {"absolute": 3}], "重叠"),
    ],
)
def test_invalid_tier_boundaries(tmp_path, tiers, fragment):
    assert any(fragment in error for error in validate_rules(_write(tmp_path, tiers)))


def test_tier_requires_absolute(tmp_path):
    assert any(
        "缺少 absolute" in error for error in validate_rules(_write(tmp_path, [{"up_to": 100}, {"absolute": 1}]))
    )
