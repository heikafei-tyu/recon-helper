import pytest

from recon.engine import run_rules


def _rules(tmp_path, left_value, right_value, tiers):
    (tmp_path / "left.csv").write_text(f"id,amount\na,{left_value}\n", encoding="utf-8")
    (tmp_path / "right.csv").write_text(f"id,amount\na,{right_value}\n", encoding="utf-8")
    path = tmp_path / "rules.yaml"
    path.write_text(
        """left: left.csv
right: right.csv
key: id
columns: [amount]
tolerance:
  amount:
    name: tiered
    tiers:
"""
        + "\n".join(
            f"      - {('name: ' + str(t['name']) + chr(10) + '        ') if t.get('name') else ''}up_to: {t.get('up_to', 'null')}\n        absolute: {t.get('absolute', 'null')}"
            for t in tiers
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def test_tolerance_uses_small_amount_band(tmp_path):
    result = run_rules(
        _rules(
            tmp_path, 100, 101, [{"name": "small", "up_to": 10000, "absolute": 1}, {"name": "large", "absolute": 100}]
        )
    )
    assert result["differences"][0]["tolerance_band"] == "small"


def test_tolerance_uses_open_ended_band(tmp_path):
    result = run_rules(
        _rules(
            tmp_path,
            200000,
            200050,
            [{"name": "small", "up_to": 10000, "absolute": 1}, {"name": "large", "absolute": 100}],
        )
    )
    assert result["differences"][0]["tolerance_band"] == "large"


@pytest.mark.parametrize(
    "tiers", ["bad", [], [{"up_to": 10}], [{"up_to": 20, "absolute": 1}, {"up_to": 10, "absolute": 1}]]
)
def test_tolerance_rejects_invalid_bands(tmp_path, tiers):
    with pytest.raises(ValueError):
        run_rules(_rules(tmp_path, 1, 2, tiers if isinstance(tiers, list) else []))
