from pathlib import Path

import pytest

from recon.plan import ExecutionPlan, PlanTask, plan_from_config


def _rules(tmp_path, name):
    left = tmp_path / f"{name}-l.csv"
    right = tmp_path / f"{name}-r.csv"
    path = tmp_path / f"{name}.yaml"
    left.write_text("id,v\na,1\n", encoding="utf-8")
    right.write_text("id,v\na,1\n", encoding="utf-8")
    path.write_text(f"left: {left.name}\nright: {right.name}\nkey: id\ncolumns: [v]\n", encoding="utf-8")
    return path


def test_plan_layers_and_run(tmp_path):
    first, second = _rules(tmp_path, "first"), _rules(tmp_path, "second")
    plan = ExecutionPlan().add(PlanTask("a", first)).add(PlanTask("b", second, ("a",)))
    result = plan.run(max_workers=1)
    assert result["layers"] == [["a"], ["b"]] and result["results"]["b"]["differences"] == []


def test_plan_parallel_layer(tmp_path):
    plan = plan_from_config([{"name": "a", "rules": "a.yaml"}, {"name": "b", "rules": "b.yaml"}], tmp_path)
    assert len(plan.layers()[0]) == 2


def test_plan_rejects_missing_dependency():
    with pytest.raises(ValueError):
        ExecutionPlan().add(PlanTask("a", Path("a"), ("missing",))).validate()


def test_plan_rejects_cycle():
    plan = ExecutionPlan().add(PlanTask("a", Path("a"), ("b",))).add(PlanTask("b", Path("b"), ("a",)))
    with pytest.raises(ValueError):
        plan.validate()


def test_plan_rejects_bad_config():
    with pytest.raises(ValueError):
        plan_from_config([])
