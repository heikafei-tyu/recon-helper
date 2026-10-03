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
