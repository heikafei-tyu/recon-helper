# 场景目录

本目录按业务用途整理当前仓库中的 50 个独立场景目录及规则演示。每个场景的实现入口位于 `examples/scenarios/`；组合场景会复用同一核对引擎，但数据和规则保持独立。

## 金融专项

| 场景 | 核对内容 | 规则类型 |
|---|---|---|
| 应收账款账龄 | 账龄分段与余额 | aging/row_compare |
| 供应商对账 | 采购、付款与余额 | row_compare |
| 库存进出平衡 | 期初+入库-出库=期末 | total_check |
| 员工报销与银行流水 | 报销单逐笔匹配流水 | row_compare |
| 多币种进出口 | 外币金额按汇率折算 | fx/row_compare |
| 跨年度滚动勾稽 | 年末与次年期初衔接 | chain_check |
| 合并报表抵消 | 内部交易抵消分录 | total_check/chain_check |
| 佣金计算 | 销售额与佣金率 | row_compare |
| 预算实际执行 | 预算、实际与偏差 | row_compare/period_check |
| 银行未达账项 | 银行单与账面差异 | row_compare |
| 部门费用环比 | 部门月度费用波动 | period_check |
| 应收应付抵消 | 往来余额双向抵消 | chain_check |
| 薪资对比率 | 薪资明细与汇总率 | row_compare |
| 库存先进先出 | 批次成本与出库成本 | row_compare |
| 项目成本归集 | 项目工时、材料、费用 | total_check |
| 合同分期收款 | 分期计划与收款流水 | chain_check |
| 汇率损益 | 期初期末汇率重估 | fx/period_check |
| 税费计算 | 税基、税率与应纳税额 | row_compare |
| 长期股权投资 | 权益法余额变动 | row_compare |
| 递延所得税 | 暂时性差异与税额 | row_compare |
| 合并范围变动 | 子公司增减持与抵消 | row_compare/chain_check |
| 收入确认时点 | 五步法控制权与确认额 | row_compare |

## 通用对账

| 场景 | 核对内容 | 规则类型 |
|---|---|---|
| accounts_offset | 往来科目抵消 | row_compare |
| aging | 通用账龄结构 | aging |
| ar_aging_check | 应收余额与账龄 | row_compare/aging |
| bank_book_outstanding | 银行账面未达 | row_compare |
| budget_actual | 预算实际 | row_compare |
| commission_reconciliation | 佣金明细 | row_compare |
| cross_sheet_new | 多 Sheet 字段 | row_compare |
| cross_year | 跨年期初期末 | chain_check |
| cross_year_rollforward | 滚动余额 | chain_check |
| deferred_tax | 税项差异 | row_compare |
| department_expense_mom | 部门环比 | period_check |
| elimination_entries | 抵消分录借贷 | total_check |
| expense_bank | 报销流水 | row_compare |
| fixed_width_payroll | 定宽工资单 | row_compare |
| foreign_translation | 外币折算 | fx/row_compare |
| fx_gain_loss | 汇兑损益 | fx/period_check |
| installment_contract | 分期收款 | chain_check |
| inventory_balance | 库存平衡 | total_check |
| inventory_fifo | FIFO 成本 | row_compare |
| missing_month | 缺失月份 | missing_check |
| multi_currency | 多币种核对 | fx/row_compare |
| multisheet | 多 Sheet 工作簿 | row_compare |
| multisheet_consolidation | 多 Sheet 合并 | total_check |
| project_cost | 项目成本 | total_check |
| quarterly | 季度汇总 | total_check/period_check |
| salary | 月薪核对 | row_compare |
| salary_ratio | 薪资比率 | row_compare |
| supplier_reconciliation | 供应商采购付款 | row_compare |
| tax_calculation | 税费计算 | row_compare |
| tsv_large_reconciliation | TSV 大文件 | row_compare |
| budget_adjustment_tracking | 预算调增调减追踪 | row_compare |
| budget_execution | 预算执行偏差 | row_compare/period_check |
| consolidated_elimination | 合并抵消分录 | total_check |
| consolidated_elimination_advanced | 多级合并抵消 | total_check/chain_check |
| consolidation_scope_change | 合并范围变动 | chain_check |
| cross_period_amortization | 跨期费用摊销 | period_check |
| deposit_flow | 保证金缴纳返还扣款 | row_compare |
| period_anomaly | 连续期间趋势异常 | period_check |
| receivable_note_endorsement | 应收票据背书链路 | chain_check |
| revenue_cost_matching | 收入成本配比 | total_check/period_check |
| revenue_recognition_timing | 收入确认时点 | row_compare |

## 教学演示

| 场景 | 核对内容 | 规则类型 |
|---|---|---|
| fixed_width_payroll_final | 定宽读取完整示例 | row_compare |
| missing_month_new | 缺失月份边界 | missing_check |
| multicurrency_import_export | 汇率日期配置 | fx |
| notification_demo | Webhook 通知 | run/notify |
| plan_demo | 依赖计划执行 | plan |
| quality_demo | 四维质量评分 | quality |
| rules_diff_demo | 规则版本差异 | rules diff |
| tiered_tolerance_demo | 多级档位容差 | tolerance |
| cross_sheet_new | 跨表列映射 | row_compare |
| quarterly | 季度汇总过程 | total_check |
| multisheet | 多 Sheet 读取 | row_compare |
| accounts_offset | 最小规则入门 | row_compare |
| deferred_tax | 财务税项示例 | row_compare |
| equity_investment | 权益法示例 | row_compare |
| foreign_translation | 折算示例 | fx |

场景测试可统一执行：`uv run --offline --with pytest --with pyyaml pytest examples/scenarios -q`。
