# YAML 配置

规则文件中的 `left` 和 `right` 是相对于规则文件目录的输入文件，`key` 是单字段关联键，`keys` 是复合关联键。两者只能使用一个。

```yaml
left: orders.csv
right: bank.csv
key: order_id
columns:
  - customer
  - amount
```

左右字段名称不一致时使用映射：

```yaml
columns:
  - left: amount
    right: total_amount
```

容差可以是单个规则，也可以是按优先级排列的规则列表：

```yaml
tolerance:
  amount:
    - name: strict
      absolute: "0.01"
      priority: 20
    - name: business
      relative: "0.005"
      round: 2
      priority: 10
```

引擎按优先级从高到低尝试，第一条命中的规则生效。`absolute` 是绝对差额，`relative` 按两边较大绝对值计算，`round` 使用四舍五入到指定小数位。

可在关联前筛选每张表：

```yaml
filters:
  left:
    - field: status
      op: eq
      value: settled
  right:
    - field: amount
      op: gte
      value: 0
```

支持 `eq`、`ne`、`in`、`contains`、`gt`、`gte`、`lt`、`lte`。字段转换在比较前执行：

```yaml
transforms:
  amount: [trim, decimal]
  customer: [trim, casefold]
```
