"""Build and execute dependency-aware reconciliation plans."""
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

from .engine import run_rules
from .parallel import run_rules_parallel


@dataclass(frozen=True)
class PlanTask:
    name: str
    rules_file: Path
    depends_on: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass
class ExecutionPlan:
    tasks: dict[str, PlanTask] = field(default_factory=dict)

    def add(self, task):
        if task.name in self.tasks:
            raise ValueError(f"计划任务重复：{task.name}")
        self.tasks[task.name] = task
        return self

    def validate(self):
        missing = {dependency for task in self.tasks.values() for dependency in task.depends_on if dependency not in self.tasks}
        if missing:
            raise ValueError(f"计划依赖不存在：{', '.join(sorted(missing))}")
        visiting, visited = set(), set()
        def visit(name):
            if name in visiting:
                raise ValueError(f"计划存在循环依赖：{name}")
            if name in visited: return
            visiting.add(name)
            for dependency in self.tasks[name].depends_on: visit(dependency)
            visiting.remove(name); visited.add(name)
        for name in self.tasks: visit(name)
        return True

    def layers(self):
        self.validate(); done, layers = set(), []
        while len(done) < len(self.tasks):
            layer = [task for name, task in self.tasks.items() if name not in done and set(task.depends_on) <= done]
            if not layer: raise ValueError("计划无法生成执行层")
            layers.append(layer); done.update(task.name for task in layer)
        return layers

    def run(self, max_workers=None):
        results, started = {}, perf_counter()
        for layer in self.layers():
            layer_results = run_rules_parallel([task.rules_file for task in layer], max_workers) if len(layer) > 1 else [run_rules(layer[0].rules_file)]
            results.update({task.name: result for task, result in zip(layer, layer_results)})
        return {"results": results, "layers": [[task.name for task in layer] for layer in self.layers()], "seconds": round(perf_counter() - started, 6)}


def plan_from_config(config, base=Path(".")):
    if not isinstance(config, list) or not config:
        raise ValueError("执行计划必须是非空任务列表")
    plan = ExecutionPlan()
    for item in config:
        if not isinstance(item, dict) or not item.get("name") or not item.get("rules"):
            raise ValueError("计划任务需要 name 和 rules")
        dependencies = tuple(item.get("depends_on", ()))
        tags = tuple(item.get("tags", ()))
        plan.add(PlanTask(item["name"], Path(base) / item["rules"], dependencies, tags))
    plan.validate(); return plan
