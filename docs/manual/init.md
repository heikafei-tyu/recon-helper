# init 命令

## 用途

`init` 通过问答生成可执行的 YAML 规则。

## 语法

```text
python -m recon init [--out FILE]
```

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| `--out` | 否 | 输出规则文件，默认 rules.yaml |

## 基本流程

向导询问左表和右表文件名。

然后询问键列和比较列。

输入绝对容差后显示完整 YAML 预览。

输入 `y` 确认写入。

输入 `n` 放弃写入。

输入 `back` 或 `上一步` 返回修改上一项。

默认规则类型是 `row_compare`。

## 示例一：行比较

交互输入：

```text
left.csv
right.csv
id
amount,status
0.01
row_compare
y
```

生成片段：

```yaml
left: left.csv
right: right.csv
key: id
columns: [amount, status]
```

## 示例二：合计检查

选择 `total_check` 后输入明细文件、汇总文件和字段。

```text
detail.csv
summary.csv
amount,quantity
```

生成片段：

```yaml
checks:
  - type: total_check
    detail: detail.csv
    summary: summary.csv
    columns: [amount, quantity]
```

## 示例三：勾稽链

选择 `chain_check`，表名用逗号分隔：

```text
jan.csv,feb.csv,mar.csv
```

并填写期初、期末字段。

## 示例四：环比

选择 `period_check`，填写文件、期间列、数值列、当前期间、上一期间和波动比例。

预览会显示完整 threshold 配置。

## 容差

绝对容差适合金额分差。

相对容差适合比例波动。

按列容差可在预览后手工补充。

输入 0 表示严格相等。

## 常见错误

空文件名会被拒绝。

字段列表为空会被拒绝。

无法解析的容差会提示重新输入。

确认输入不是 `y` 时不会落盘。

输出目录不存在会自动创建。

金融规则缺字段时请使用 `back` 返回修改。

生成后建议执行 `python -m recon validate rules.yaml`。

规则路径中的中文可直接输入。

向导不上传文件，也不会修改输入表。

生成的 YAML 使用 UTF-8 和中文安全格式。

复杂规则可先向导生成，再手工编辑。

更多运行方法见 [run.md](run.md)。
