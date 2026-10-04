# 执行计划

`recon.plan` 将多个规则文件组织成有依赖关系的任务图。没有依赖的任务会在同一层并行执行，后续层会等待前置任务完成。

## 命令行执行

计划文件可以是任务数组，也可以使用 `tasks` 包裹：

```yaml
tasks:
  - name: sales
    rules: rules/sales.yaml
  - name: cash
    rules: rules/cash.yaml
    depends_on: [sales]
```

运行 `python -m recon plan plan.yaml --attempts 3 --timeout 60 --fail-fast`。
命令输出每个任务的状态、尝试次数和事件列表；失败任务不会出现在
`results` 中，`--fail-fast` 会阻止后续任务继续启动。

任务配置包含 `name`、`rules`、可选 `depends_on` 和 `tags`。执行前会检查重复名称、缺失依赖和循环依赖。`ExecutionPlan.run(max_workers=...)` 返回每个任务的核对结果、执行层和总耗时。

该模块适合把月度明细核对、汇总核对和报表检查组织成稳定的业务顺序；它不会修改规则文件或输入数据。
