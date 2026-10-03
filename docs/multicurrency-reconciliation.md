# 多币种核对

规则可声明带日期的汇率：

```yaml
currency:
  as_of: 2024-01-10
  max_age_days: 30
  rates:
    USD/CNY: {rate: 7.2, date: 2024-01-01}
```

缺少币种对或汇率为非正数会立即报错；报价日期距离核对日期超过 `max_age_days` 时报告汇率过期。日期口径应统一使用 ISO `YYYY-MM-DD`。
### 汇率审计

`FXRates.validate_quotes` 接受包含 `currency`、`date`、`rate` 的报价列表，并返回审计结果。报价日期距 `as_of` 超过 `max_age_days` 时返回 `rate_expired`；同一币种同一交易日出现不同正汇率时返回 `rate_conflict`。字段缺失、日期非法、非正汇率会抛出 `ValueError`，避免静默采用错误报价。
