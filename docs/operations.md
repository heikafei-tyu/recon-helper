# 运营与治理

批次执行用于把多个独立规则作为一次运营任务运行：

```python
from recon.operations import run_batch
result = run_batch(["rules/sales.yaml", "rules/cash.yaml"], "recon_history.db")
```

每个条目都有 `passed`、`differences` 或 `failed` 状态、耗时、差异数和历史
记录 ID。失败任务默认不阻止后续任务；需要严格顺序时设置 `stop_on_error=True`。

`history_summary` 返回运行总数、累计差异、致命运行次数和按日期聚合的趋势，
可直接提供给 Web 仪表盘。`review_queue` 展开所有尚未处理的差异，供复核人员
按严重程度和历史 ID 处理。`export_history` 生成脱敏前的本地审计快照，输出
前应确认数据库中没有客户敏感信息。
