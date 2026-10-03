# 账龄分析

`aging_structure` 按到期日和核对日将余额放入 0-30、0-60、0-90、0-180、0-360 和 360+ 区间，返回各段金额与占比。`compare_aging` 接受两期结构，输出每个区间占比变化，用于识别逾期结构恶化。

`compare_aging(current, previous, threshold="0.05")` 会在变化超过阈值时增加 `assessment`。较老区间占比上升标记为“账龄恶化”，占比下降标记为“账龄改善”，其余为“稳定”，并保留 current_ratio、previous_ratio、change 和 threshold，便于报告审计。阈值必须是非负数字。
