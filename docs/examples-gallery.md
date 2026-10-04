# 场景目录

`examples/scenarios/` 中的每个业务目录都包含输入数据、规则和 `expected.json`。
独立测试文件验证该场景的预期结果。

| 场景 | 用途 |
|---|---|
| `salary` / `salary_ratio` | 工资明细、净薪资比例核对 |
| `supplier_reconciliation` | 采购与供应商付款核对 |
| `inventory_balance` / `inventory_fifo` | 库存平衡与先进先出 |
| `project_cost` | 项目材料、人工、间接费用归集 |
| `installment_contract` | 合同分期本金、利息和收款核对 |
| `fx_gain_loss` / `multicurrency_import_export` | 汇率重估和多币种金额 |
| `tax_calculation` | 税基、税率和税额计算 |
| `quality_demo` | 干净表与脏表质量评分对比 |
| `tiered_tolerance_demo` | 金额档位容差命中 |
| `rules_diff_demo` | 两版 YAML 规则差异 |
| `plan_demo` | 依赖计划分层执行 |
| `notification_demo` | Webhook 摘要通知模拟 |
| `fixed_width_payroll_final` | 固定宽度工资单读取 |
| `missing_month` / `period_anomaly` | 缺失期间和波动异常 |
| `aging` / `ar_aging_check` | 应收账龄和账龄结构 |
| `bank_book_outstanding` | 银行对账未达账项 |

运行全部场景测试：`python -m pytest examples/scenarios tests/test_scenarios.py -q`。
场景数据均为本地构造样例，不代表真实客户数据。
