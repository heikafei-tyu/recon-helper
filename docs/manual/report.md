# report 命令

## 用途

`report` 执行核对并生成 Excel 或 HTML 报告。

## 语法

```text
python -m recon report RULES [--out FILE] [--html FILE] [--incremental] [--force]
```

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| `RULES` | 是 | YAML 规则文件 |
| `--out` | 否 | Excel 输出路径，默认 output/reconciliation.xlsx |
| `--html` | 否 | 输出交互式 HTML 路径 |
| `--incremental` | 否 | 输入未变化时跳过 |
| `--force` | 否 | 覆盖已存在报告 |

## Excel 内容

Summary 页显示核对行数、差异数和结论。

Differences 页显示全部差异。

每个参与文件有独立明细页。

差异行使用黄色底纹。

汇总页包含差异分布图表（安装 matplotlib 时）。

## 示例一：Excel

```powershell
python -m recon report examples/rules.yaml --out output/orders.xlsx
```

输出片段：

```json
{"output":"output/orders.xlsx","differences":3,"skipped":false}
```

## 示例二：HTML

```powershell
python -m recon report examples/rules.yaml --html output/orders.html
```

HTML 支持按表筛选、按严重程度筛选和差异排序。

## 示例三：增量

第一次运行：

```powershell
python -m recon report rules.yaml --out output/a.xlsx --incremental
```

输入未变化时再次运行输出片段：

```json
{"skipped":true,"reason":"inputs unchanged"}
```

## 示例四：覆盖

报告已存在时：

```powershell
python -m recon report rules.yaml --out output/a.xlsx --force
```

`--force` 会重新计算并替换报告。

## 常见错误

`RECON_REPORT_ERROR` 表示输出目录不可写或规则执行失败。

输出目录不存在时工具会创建目录。

文件被 Excel 锁定时关闭工作簿后重试。

未安装 openpyxl 时安装 requirements.txt。

未安装 matplotlib 时仍可生成无图表报告。

不使用 `--force` 不会覆盖已有文件。

增量清单与报告放在同一目录，需保留清单文件。

修改规则后指纹变化，会重新核对。

HTML 是静态文件，可直接用浏览器打开。

报告只包含当前上传文件的数据，不会联网。

建议先用 `run` 检查规则，再生成报告。

更多输入格式见 [read.md](read.md)。
