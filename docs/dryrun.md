# dryrun 调试

使用 `python -m recon dryrun rules.yaml` 调试一条左右表规则。命令只读取输入
和规则，不写 SQLite、不生成报告，也不会发送通知。

输出包含左右表的列和行数摘要、成功匹配的键，以及每个键每个比较列的原始
值、标准化值、差值和相等判断。左右表只有一边存在的键会输出 `matched=false`
及原因，适合检查键列拼写、数字格式和列映射。

`dryrun` 当前面向 `left/right/key(s)/columns` 规则；合计、勾稽和缺失检测等
多表检查应使用 `run` 或 `report` 执行。
