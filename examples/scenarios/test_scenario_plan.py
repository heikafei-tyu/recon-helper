from pathlib import Path
import yaml
from recon.plan import plan_from_config

def test_plan_scenario():
    root = Path(__file__).parent / "plan_demo"
    config = yaml.safe_load((root / "plan.yaml").read_text(encoding="utf-8"))
    result = plan_from_config(config["tasks"], root).run(max_workers=1)
    assert result["layers"] == [["detail"], ["summary"], ["final"]]
    assert all(not value["differences"] for value in result["results"].values())
