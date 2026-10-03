# 容差指南

```yaml
tolerance:
  default: {absolute: "0.01", rounding: {mode: cents, digits: 2}}
  amount:
    - {name: strict, absolute: "0.01", priority: 20}
    - {name: relative, relative: "0.005", priority: 10}
```

`absolute` 和 `relative` 取较宽阈值；按列配置覆盖 default。`raw` 直接比较原始 Decimal，`cents` 或 `decimal` 使用 ROUND_HALF_UP 后比较。优先级高的规则先尝试，报告会保留命中规则和被忽略规则。

输入数字支持千分位、货币符号和百分比。单位换算使用 `units` 配置，比较前统一到 `target`。
