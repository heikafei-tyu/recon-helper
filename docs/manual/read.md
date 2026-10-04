# read 命令

## 用途

`read` 读取 CSV、TSV、JSON 或 XLSX，并输出结构摘要。

## 语法

```text
python -m recon read FILE [--encoding ENCODING] [--sheet-name NAME] [--sheet-index N]
```

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| `FILE` | 是 | 输入文件路径 |
| `--encoding` | 否 | 强制编码，如 utf-8、gbk、utf-16 |
| `--sheet-name` | 否 | XLSX 工作表名称 |
| `--sheet-index` | 否 | XLSX 工作表序号，从 0 开始 |

## 输出字段

输出 JSON 包含 `row_count`、`columns`、`types`。
`row_count` 不包含表头。
`columns` 保持文件中的原始顺序。
`types` 是推断类型，不会修改源文件。

## 示例一：CSV

输入 `orders.csv`：

```csv
order_id,amount
A001,120.50
A002,80
```

命令：

```powershell
python -m recon read orders.csv
```

输出片段：

```json
{"row_count":2,"columns":["order_id","amount"],"types":{"order_id":"string","amount":"number"}}
```

## 示例二：GBK

输入为 GBK 编码的 `销售.csv`。

```powershell
python -m recon read 销售.csv --encoding gbk
```

输出片段：

```json
{"row_count":35,"columns":["日期","部门","金额"]}
```

## 示例三：XLSX 工作表

```powershell
python -m recon read books.xlsx --sheet-name 明细
```

输出片段：

```json
{"row_count":120,"columns":["凭证号","科目","借方","贷方"]}
```

也可以使用 `--sheet-index 1` 读取第二张表。

## 示例四：JSON

输入 `orders.json` 为对象数组：

```json
[{"id":"A1","amount":10},{"id":"A2","amount":20}]
```

```powershell
python -m recon read orders.json
```

输出片段：

```json
{"row_count":2,"columns":["id","amount"]}
```

## 常见错误

`RECON_READ_ERROR` 表示文件不可读或格式不正确。

文件不存在时检查当前目录和相对路径。

中文乱码时尝试 `--encoding gbk` 或 `--encoding utf-16`。

XLSX 工作表不存在时先用 Excel 查看准确的工作表名称。

空文件没有表头，需补充第一行字段名。

重复列名会被拒绝，应在源表中改成唯一列名。

JSON 必须是非空对象数组，不支持单个对象。

CSV 每行字段数量必须与表头一致。

公式单元格应先在 Excel 中保存为已计算的数值。

读取成功后可把摘要保存到日志：

```powershell
python -m recon read orders.csv > output/read.json
```

建议先执行 `read` 再编写规则，以免列名拼写不一致。

`--sheet-index` 默认值为 0。

编码参数只影响文本解码，不会改变数字格式。

大 CSV 读取摘要仍会逐行处理，适合先做结构检查。

遇到异常请保留完整错误前缀和输入文件类型。

更多规则示例见 [run.md](run.md)。
# read：读取表格

`read` 输出输入文件的列名、行数和类型推断，是运行核对前的快速体检命令。

## 支持格式

| 扩展名 | 读取方式 | 备注 |
|---|---|---|
| `.csv` | 自动识别编码 | 支持 UTF-8、GBK 等常见编码 |
| `.tsv` | 制表符分隔 | 与 CSV 相同的类型推断 |
| `.json` | 对象数组 | 每个对象对应一行 |
| `.xlsx` | openpyxl | 支持工作表、表头偏移和只读模式 |
| `.xls` | xlrd | 支持旧版 Excel 日期序列号 |
| `.ods` | OpenDocument XML | 无需 LibreOffice，解析 `content.xml` |
| `.xml` | 行列式 XML | 支持 `row/cell`、`record/field` 结构 |
| `.parquet` | pyarrow | 保留列类型映射 |

## 语法

```powershell
recon read <文件>
```

示例：

```powershell
recon read examples/orders.csv
# 行数: 3
# 列: order_id, amount, status
```

```powershell
recon read data/monthly.ods
# 格式: ods
# 工作表: Sheet1
```

```powershell
recon read data/export.xml
# 类型: xml
# 列: id, amount
```

## 常见错误

- 文件不存在：检查路径和当前工作目录。
- 扩展名不支持：将文件转换为支持格式，或确认扩展名没有拼写错误。
- ODS 损坏：确认压缩包内存在 `content.xml`，不要把导出的 PDF 重命名为 `.ods`。
- XML 没有行数据：将记录组织为 `row/cell` 或 `record/field` 元素，并把第一行作为表头。
- 列数不一致：补齐缺失单元格或修正导出程序的列布局。

读取成功后再执行 `recon run`，可避免把格式问题误判为业务差异。
