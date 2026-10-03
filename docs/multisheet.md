# 多 Sheet 核对

XLSX 规则可用 `left_sheet` 和 `right_sheet` 指定工作表：

```yaml
left: ledger.xlsx
right: report.xlsx
left_sheet: 明细
right_sheet: 汇总
key: account
columns: [amount]
```

`recon read` 默认读取第一个 Sheet；报告会保留来源表信息。
