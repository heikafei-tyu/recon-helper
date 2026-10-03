# 规则语法

## 两表核对

```yaml
left: orders.csv
right: bank.csv
key: order_id
columns:
  - amount
  - {left: quantity, right: count}
```

路径相对规则文件所在目录。`keys` 可替代 `key` 指定复合键；`left_sheet` 和 `right_sheet` 可选择 XLSX 工作表。`filters` 在建索引前过滤记录，`transforms` 可配置字段清洗。

## 金融检查

`checks` 支持 `total_check`、`chain_check`、`missing_check`。合计检查指定 `detail`、`summary`、`columns`；勾稽链指定有序 `tables`、`start_column`、`end_column`；缺失检查指定 `file`、`time_column`、`frequency`。

## 命令

```powershell
python -m recon validate rules.yaml
python -m recon run rules.yaml
python -m recon report rules.yaml --out output/report.xlsx
```
