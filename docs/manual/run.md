# run 命令

## 用途

`run` 按 YAML 规则比较两张表，或执行金融检查规则。

## 语法

```text
python -m recon run RULES [--progress] [--timeout SECONDS]
```

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| `RULES` | 是 | YAML 规则文件 |
| `--progress` | 否 | 输出处理进度 |
| `--timeout` | 否 | 超时秒数，超时返回 2 |

## 行比较规则

```yaml
left: orders.csv
right: bank.csv
key: order_id
columns: [amount, status]
```

`left`、`right` 相对于规则文件所在目录解析。

`key` 是唯一关联键，也支持 `keys: [部门, 月份]`。

`columns` 列出需要比较的字段。

## 示例一：无差异

输入两张相同的订单表。

```powershell
python -m recon run examples/rules.yaml
```

输出片段：

```json
{"left_rows":2,"right_rows":2,"differences":[]}
```

## 示例二：金额差异

左表 A001 为 100，右表为 101。

```powershell
python -m recon run rules.yaml
```

输出片段：

```json
{"key":"A001","column":"amount","left":100,"right":101,"difference":"-1"}
```

## 示例三：金融合计

```yaml
checks:
  - type: total_check
    detail: detail.csv
    summary: summary.csv
    columns: [amount]
```

```powershell
python -m recon run finance.yaml
```

输出片段：

```json
{"status":"total_mismatch","column":"amount","difference":"10"}
```

## 示例四：勾稽链

```yaml
checks:
  - type: chain_check
    tables: [jan.csv, feb.csv, mar.csv]
    start_column: 期初
    end_column: 期末
```

三张表按顺序比较上一张期末与下一张期初。

## 容差

可配置全局绝对容差：

```yaml
tolerance:
  default: {absolute: "0.01"}
```

也可按列使用相对容差和舍入口径。

命中容差的差异不会进入结果。

## 常见错误

`RECON_RULE_ERROR` 表示规则结构或列名错误。

left/right 缺失时补齐文件名。

key 不存在时先用 `read` 检查表头。

复合键必须使用 `keys` 列表。

columns 必须是非空列表。

金额不能解析时清理货币符号或配置数字转换。

timeout 过小时增加秒数或使用分批文件。

文件路径按规则文件目录解析，不按当前 shell 目录解析。

`--progress` 适合大文件，输出到标准输出。

结果中的行号包含表头，便于定位 Excel 行。

更多容差说明见 [report.md](report.md)。
