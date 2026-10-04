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

## 可恢复执行

计划执行会把运行状态写入 `recon_history.db` 的 `plan_runs` 和 `plan_tasks` 表。
每次运行可使用幂等键，重复提交同一个幂等键会复用原运行记录，避免重复写入：

```powershell
recon plan plan.yaml --attempts 3 --timeout 60 --idempotency-key 2026-10-close
```

计划状态可通过以下命令查看：

```powershell
recon plan --status
```

状态含义：`pending` 表示尚未启动，`running` 表示正在执行，`success` 表示所有任务完成，
`stopped` 表示启用了 `--fail-fast` 并在失败后停止。运行记录包含总耗时和错误摘要，
任务记录包含每个任务的状态、尝试次数、耗时和错误信息。

当进程在任务中途退出时，可以使用原计划文件和同一个幂等键重新运行。已经成功的任务
会被识别并跳过，失败或未开始的任务按新的重试策略继续执行。若需要明确指定已有运行记录，
可使用 `--run-id`，适合运维脚本在保存运行编号后恢复。

重试次数包含首次执行，例如 `--attempts 3` 最多执行三次。`--timeout` 是单次尝试的秒数；
超时会记录为 `timeout`，并在仍有剩余尝试时继续重试。建议在规则文件访问外部存储时设置
超时，避免一个任务长期占用整个计划。
