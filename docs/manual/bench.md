# bench 命令

## 用途

`bench` 测量 CSV 流式读取的耗时、行数、重复键和内存。

## 语法

```text
python -m recon bench [FILE] [--key COLUMN] [--no-duplicate-check] [--timeout SECONDS] [--progress] [--json-out FILE]
```

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| `FILE` | 否 | CSV 文件；省略时生成 100000 行样例 |
| `--key` | 否 | 重复检查列，默认 id |
| `--no-duplicate-check` | 否 | 关闭重复键统计 |
| `--timeout` | 否 | 超时秒数 |
| `--progress` | 否 | 显示百分比进度 |
| `--json-out` | 否 | 将结果写入 JSON |

## 示例一：现有文件

```powershell
python -m recon bench examples/orders.csv --key order_id
```

输出片段：

```json
{"rows":1200,"duplicate_keys":0,"elapsed_seconds":0.04}
```

## 示例二：自动生成

```powershell
python -m recon bench --progress
```

输出片段：

```json
{"rows":100000,"streaming_peak_bytes":...,"full_load_estimate_bytes":...}
```

## 示例三：保存结果

```powershell
python -m recon bench examples/orders.csv --json-out output/bench.json
```

输出文件可以用于设计文档或 CI 趋势比较。

## 示例四：关闭重复检查

```powershell
python -m recon bench large.csv --no-duplicate-check
```

关闭后减少集合内存，适合只关心吞吐量的测试。

## 性能解释

流式读取一次只保留当前行和统计状态。

峰值内存通常与文件总行数无关。

重复检查开启时，键集合会随唯一键增长。

CSV 编码检测会增加少量启动耗时。

## 常见错误

`RECON_BENCH_ERROR` 表示文件或列不存在。

key 列拼写错误时使用 `read` 查看表头。

timeout 太短时增加秒数。

超时返回退出码 2 和 `RECON_TIMEOUT`。

二进制或 XLSX 文件不能直接作为 bench 输入。

带引号的 CSV 会按标准 csv 模块解析。

进度输出会增加少量 I/O，正式基准可关闭 `--progress`。

建议在同一机器重复三次取中位数。

结果中的内存值是估算或采样值，不等于操作系统常驻集全部。

更多大文件策略见项目 design.md。

示例：

```powershell
python -m recon bench examples/orders.csv --key order_id --timeout 30
```
