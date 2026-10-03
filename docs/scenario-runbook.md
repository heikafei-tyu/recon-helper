# 场景运行手册

每个 `examples/scenarios/*` 目录都包含数据、规则、预期输出和 `run_scenario.py`。在仓库根目录执行：

```powershell
python examples/scenarios/salary/run_scenario.py
python examples/scenarios/missing_month/run_scenario.py
```

脚本输出 JSON，适合人工查看和 CI 比对。
