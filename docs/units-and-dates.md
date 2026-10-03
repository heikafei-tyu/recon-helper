# 单位与日期

金额字段可在比较前统一单位：

```yaml
units:
  amount: {left: 万元, right: 元, target: 元}
```

支持元、万元、亿元和 USD（USD 需提供 `rates: {USD: 7.2}`）。日期支持 `YYYY-MM-DD`、`YYYY/M/D` 和 `YYYYMMDD`，统一为 ISO 日期后比较。
