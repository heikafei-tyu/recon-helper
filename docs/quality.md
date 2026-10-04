# 数据质量评分

报告生成时会对规则中的左右输入表分别评分。评分范围为 0 到 100，四个
维度各占 25 分：空值率、类型错误率、重复率和主键唯一性。每个维度按
错误比例扣分，报告汇总页会列出得分；低于 `quality.threshold` 的输入表
以红色标记。

```yaml
quality:
  threshold: 80
keys: [account_id]
```

也可以在 Python 中直接调用 `assess_file(path, key_columns, expected_types)`。
`expected_types` 支持 `number`、`integer`、`date` 和 `text`。返回值包含
`dimensions`、`deductions`、`score` 和 `passed`，适合接入自定义报告或门禁。
