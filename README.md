# recon-helper 对账核对工具

## 是什么
一个本地命令行工具：读取多份表格（xlsx/csv/json），按规则做跨表核对（数字对不对得上），自动找出差异并生成核对报告。

## 当前能力

- M1：读取 xlsx、CSV、JSON，识别 UTF-8、GBK 和 UTF-16。
- M2：用 YAML 指定两张表、关联键和比较字段。
- M3：按列配置绝对/相对容差和四舍五入。
- M4：逐行读取 CSV 并运行基准统计。
- M5：生成带明细、汇总和高亮的 Excel 报告，支持增量跳过。

输入文件只在本机处理；示例数据均为虚构数据。

## 解决什么问题
人工核对多张 Excel 报表耗时易错（差 2 万是算错、舍入还是漏单？），本工具自动定位"哪一行哪一列、差多少、大概率什么原因"。

## 当前状态
M0–M5 均已实现：读取、规则、容差、性能基准和 Excel 报告。当前版本包含复合键、字段映射、规则预检查、优先级容差和增量报告。

## 安装
Python 3.10+，在仓库目录执行：
```powershell
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

开发环境还可安装 `requirements-dev.txt`，其中包含 pytest、ruff 和构建工具。
新环境的最短安装流程见 [docs/quickstart.md](docs/quickstart.md)。

## 运行
```powershell
recon read examples/orders.xlsx
python -m recon read examples/orders-gbk.csv
python -m recon read examples/orders-utf16.csv
python -m recon read examples/orders.json
python -m pytest -q
python -m recon run examples/rules.yaml
python -m recon bench examples/orders.csv --key order_id
python -m recon bench examples/orders.csv --key order_id --progress
python -m recon bench --progress
python -m recon run examples/rules.yaml --progress --timeout 30
python -m recon validate examples/rules.yaml
python -m recon report examples/rules.yaml --out output/reconciliation.xlsx
python -m recon report examples/rules.yaml --html output/reconciliation.html
python -m recon report examples/rules.yaml --out output/reconciliation.xlsx --incremental
```

## 服务模式

安装 `fastapi`、`httpx` 后运行 `uvicorn recon.api:app --reload`。服务提供 `POST /reconcile` 上传表格和规则并返回差异 JSON，`GET /history` 查询快照，`GET /docs` 查看自动生成的 API 文档。命令行 `recon init` 会交互式询问表名、键列、比较列和容差，确认后生成 `rules.yaml`。

金融报表检查可在规则文件中使用 `checks`：

```yaml
checks:
  - type: total_check
    detail: detail.csv
    summary: summary.csv
    columns: [amount, quantity]
  - type: chain_check
    tables: [january.csv, february.csv, march.csv]
    start_column: 期初
    end_column: 期末
  - type: missing_check
    file: monthly.csv
    time_column: month
    frequency: month
    start: 2026-01
    end: 2026-12
```

`total_check` 以汇总表最后一行作为合计行；`chain_check` 按表顺序比较前表期末与后表期初；`missing_check` 支持 `month` 和 `day`，省略起止时间时按实际数据的最小、最大值检查中间缺口。运行方式仍是 `python -m recon run finance-rules.yaml`。

两表规则的完整写法如下：

```yaml
left: orders.csv
right: bank.csv
key: order_id
columns: [amount, quantity]
tolerance:
  default: {absolute: "0.01", rounding: {mode: cents, digits: 2}}
  amount: {relative: "0.001", priority: 10}
```

完整命令包括 `read`（读取摘要）、`run`（执行核对）、`validate`（预检查规则）、`bench`（流式性能基准）和 `report`（Excel/HTML 报告）。Excel 报告的第一页是 Summary，后续包含总差异页和每个参与文件的差异明细页；`--incremental` 根据规则及所有参与文件的 SHA-256 指纹跳过未变化的核对，`--force` 覆盖已有报告。
读取首个 XLSX 工作表、带表头的 CSV/TSV、非空对象数组 JSON；可用 `--sheet-name` 或 `--sheet-index` 选择 XLSX 工作表。
列名须非空且唯一，每行字段须一致。标识符保留前导零，空值统一为 null。
编码自动支持 UTF-8、GBK、带 BOM 的 UTF-16；存在歧义时用 `--encoding` 指定。
XLSX 公式会报错，须先转换为已核验的数值。类型推断仅用于摘要，不改变单元格文本。

## 运行产物
当前输出 JSON 摘要：row_count、columns、types；输入错误返回退出码 2。
examples 中所有数据为虚构示例，运行 `python examples/generate.py` 可重新生成。
规则包含 left/right 文件路径（相对于规则文件）、唯一关联键 key 和比较字段列表 columns。
run 输出 JSON 差异，包括键、表名、源表行号（含表头）、字段、两边值和数值差额（左减右）；缺失记录分别标为 left_only/right_only。
字段可解析为有限数值时按 Decimal 比较，否则比较文本；容差规则按优先级逐条尝试，关联键按原始文本精确匹配。
bench 使用逐行 CSV 读取，输出行数、重复键数、耗时和峰值内存；省略文件参数会自动生成 100000 行样例并输出流式结果与全量载入理论对照。`run --progress` 输出处理进度百分比，`--timeout` 超时返回 `RECON_TIMEOUT`。
report 命令生成 Differences 和 Summary 工作表；使用 `--incremental` 可在输入哈希未变化时跳过。

## 目录结构

### 业务场景示例

`examples/scenarios/` 包含独立数据、规则、预期结果和测试的真实业务结构示例：应收账款账龄、供应商对账、库存进出平衡、员工报销与银行流水、多币种进出口、跨年度滚动、合并报表抵消、佣金计算、预算与实际执行、银行对账单与账面（含未达账项）。可从仓库根目录运行 `pytest tests/test_scenario_01.py tests/test_scenario_10.py` 验证单个场景，或运行 `pytest tests/test_scenarios.py` 扫描全部场景。

`recon/` 是源码，`tests/` 是单元和集成测试，`examples/` 是可运行的虚构输入，`design.md` 记录设计取舍，`docs/` 预留扩展文档位置。

## 错误码

成功返回 `0`；输入、规则、报告和基准命令的用户错误返回 `2`，并分别使用 `RECON_READ_ERROR`、`RECON_RULE_ERROR`、`RECON_REPORT_ERROR` 和 `RECON_BENCH_ERROR` 前缀。

## 验证和构建

```powershell
python -m pytest -q
python -m build
```

GitHub Actions 会在 push 和 pull request 时重复测试并构建 wheel。提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [SECURITY.md](SECURITY.md)。
