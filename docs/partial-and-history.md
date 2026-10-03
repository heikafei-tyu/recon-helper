# 部分核对、分级与历史

范围配置示例：

```yaml
scope:
  first_n: 100
  department: 财务部
  department_column: department
  date_from: 2024-01-01
  date_to: 2024-03-31
```

差异分为致命、严重、提示：缺数据为致命，超容差为严重，容差内为提示。历史快照保存规则、输入 SHA-256 和结果摘要，可使用 `python -m recon history --dir history` 查看。
