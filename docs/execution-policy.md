# 执行策略

`recon.execution` 为计划任务和定时任务提供统一的执行包装器。

## RetryPolicy

`attempts` 是总尝试次数，包含第一次执行，默认值为 1。
`delay` 是两次尝试之间的秒数，默认不等待。
`timeout` 是单次尝试的秒数，省略时不设超时。

```python
from recon.execution import RetryPolicy, execute

policy = RetryPolicy(attempts=3, delay=0.2, timeout=30)
report = execute("monthly-reconcile", run_monthly, policy)
```

## 报告与事件

`ExecutionReport.status` 为 `success` 或 `failed`。超时会在事件中标记为
`timeout`，最终报告仍使用 `failed`，这样调用方只需要处理一种失败状态。
每个尝试都会生成一个 `ExecutionEvent`，包含任务名、序号、开始时间、耗时
和错误文本，可直接转成日志或写入 SQLite。

## 批量执行

`execute_many` 接收 `(name, action)` 二元组列表，保持输入顺序返回报告。
`fail_fast=True` 时第一个失败会停止后续任务；默认会继续执行剩余任务。

```python
reports = execute_many([
    ("sales", lambda: run_rules("sales.yaml")),
    ("cash", lambda: run_rules("cash.yaml")),
], RetryPolicy(attempts=2), fail_fast=False)
```

动作抛出的异常不会向外传播，而会写入报告的 `error` 和对应事件，适合
调度器继续运行并在历史记录中展示失败原因。超时使用独立线程等待，动作
本身应避免修改无法回滚的共享资源。
