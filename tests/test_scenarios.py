import json
from pathlib import Path

import pytest

from recon.engine import run_rules

SCENARIOS = sorted(
    path
    for path in Path(__file__).parents[1].glob("examples/scenarios/*")
    if path.is_dir()
    and (path / "rules.yaml").exists()
    and (path / "expected.json").exists()
    and isinstance(json.loads((path / "expected.json").read_text(encoding="utf-8")).get("differences"), list)
)


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda path: path.name)
def test_business_scenario(scenario):
    result = run_rules(scenario / "rules.yaml")
    expected = json.loads((scenario / "expected.json").read_text(encoding="utf-8"))
    actual = result["differences"]
    assert len(actual) == len(expected["differences"])
    for actual_row, expected_row in zip(actual, expected["differences"]):
        assert all(actual_row.get(key) == value for key, value in expected_row.items())
