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

也可以使用显式形式 `python -m recon plan run plan.yaml --attempts 2`。程序会
先校验重复任务、缺失依赖和循环依赖，再按依赖层执行；每个任务的失败、重试
和超时事件都会出现在 JSON 输出中。

使用 `python -m recon rules diff old.yaml new.yaml` 比较两版规则。输出包括
`added`、`removed`、`changed` 三组清单，并以字段路径显示 `keys`、`columns`
和 `tolerance` 的具体变化，适合在提交规则前复核口径。
