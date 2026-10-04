# recon-helper

本地优先的财务与业务报表核对工具。读取 CSV、TSV、JSON、XLSX，按 YAML 规则定位缺失、金额差异、合计错误和跨期勾稽问题，并生成可审计报告。

## 功能特性

1. 多格式读取；2. UTF-8/GBK/UTF-16 自动识别；3. 单键和复合键；4. 按列比较；5. 绝对容差；6. 相对容差；7. 金额档位容差；8. 按列优先级；9. 舍入后比较；10. 数字归一化；11. 合计核对；12. 多表勾稽；13. 月日缺失检测；14. 环比同比检查；15. 多币种换算；16. 部分范围核对；17. 差异分级；18. 流式读取；19. 进度与超时；20. Excel/HTML 报告；21. 增量指纹；22. 历史快照；23. 差异复核；24. 数据质量评分；25. Webhook/SMTP 通知；26. 依赖计划执行；27. dryrun 调试；28. 规则版本对比；29. FastAPI 服务；30. Web 规则编辑器；31. 核对仪表盘；32. 配置 Profile；33. 自定义插件；34. 交互式向导；35. 调度器定时执行；36. 调度运行日志；37. 运维批次编排；38. 运维历史汇总；39. 复核队列；40. SQLite 结果持久层；41. API Key 鉴权；42. 审计日志；43. 质量评分 Excel 页签；44. 报告模板切换；45. TSV/定宽/XLS/Parquet 读取；46. 并行规则执行；47. 规则校验器；48. 模糊列名匹配；49. 重复行检测；50. 列画像；51. 离群值检测；52. Schema 校验；53. 汇率日期检查；54. 历史核对对比；55. 交互式 HTML 筛选；56. 结果通知强制告警；57. 场景目录索引；58. 长期股权投资与收入确认专项场景。

## 快速开始

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
python -m recon read examples/orders.csv
python -m recon run examples/rules.yaml
python -m recon report examples/rules.yaml --out output/reconciliation.xlsx
python -m recon run examples/rules.yaml --notify-webhook https://hooks.example.test/recon
python -m pytest -q
```

## 命令总览

| 命令 | 作用 | 说明 |
|---|---|---|
| `read` | 表结构摘要 | [read](docs/manual/read.md) |
| `run` | 执行核对 | [run](docs/manual/run.md) |
| `report` | Excel/HTML 报告 | [report](docs/manual/report.md) |
| `bench` | 性能基准 | [bench](docs/manual/bench.md) |
| `history` | 核对快照 | [history](docs/manual/history.md) |
| `init` | 规则向导 | [init](docs/manual/init.md) |
| `validate` | 规则预检查 | [run](docs/manual/run.md) |
| `profile` | 配置预设 | [profiles](docs/profiles.md) |

## 最小规则

```yaml
left: orders.csv
right: bank.csv
key: order_id
columns: [amount, status]
tolerance:
  default: {absolute: "0.01"}
```

路径相对于规则文件目录解析。建议先执行 `python -m recon read FILE` 再填写列名。

## 金融规则

```yaml
checks:
  - type: total_check
    detail: detail.csv
    summary: summary.csv
    columns: [amount]
  - type: chain_check
    tables: [jan.csv, feb.csv]
    start_column: 期初
    end_column: 期末
```

## 服务模式

安装 FastAPI 后执行 `uvicorn recon.api:app --reload`；使用 `POST /reconcile` 核对文件，`GET /history` 查看历史，`GET /docs` 查看 Swagger。

Web 页面支持上传核对、历史筛选、结果排序和静态资源导出入口；调度器可用 `recon schedule start/stop/list` 管理定时规则。老式 XLS、Parquet 和固定宽度输入均可通过 `recon read` 读取。

## Web 界面

启动 `uvicorn recon.api:app --reload` 后打开 `http://127.0.0.1:8000/`。核对页可上传左右表和 YAML 规则并显示分级差异；历史页查看已保存的核对记录；报告页提供报告生成入口。结果和差异会写入本地 `recon_history.db`，无数据库时 `history` 命令自动回退到 `history/*.json`。

规则编辑器位于 `/web/rules`，仪表盘位于 `/web/dashboard`；页面模板在 `templates/`，浏览器资源在 `recon/static/`。

API `POST /reconcile` 支持 `page` 和 `page_size` 分页参数，`GET /history` 支持
`from_date`、`to_date` 日期过滤以及 `limit`/`offset` 分页。完整说明见
[Web 文档](docs/web.md)。

## FAQ

- 中文乱码：`read --encoding gbk`。
- 找不到列：先运行 `read` 复制准确表头。
- 报告无法覆盖：关闭 Excel 或使用 `--force`。
- 大文件内存高：使用 `bench`，必要时关闭重复检查。
- 生成规则：执行 `python -m recon init`。

详见 [FAQ](docs/faq.md) 和 [故障排查](docs/troubleshooting.md)。

## 数据质量与通知

报告会按空值率、类型错误率、重复率和主键唯一性对左右输入表评分，配置
`quality.threshold` 可设置红色告警阈值。`recon run` 支持 `--notify-webhook`
或 SMTP 参数推送完成摘要；出现致命差异时会强制通知。详见
[质量评分](docs/quality.md) 和 [通知](docs/notify.md)。

## 场景与安全

`examples/scenarios/` 包含应收账款、供应商、库存、报销、跨年度、预算、银行等独立业务场景，每个目录都有规则、预期结果和测试。数据默认只在本机处理；共享前请清理密钥、客户信息、内部地址和真实账号。

完整的 58 个场景分类索引见 [场景目录](docs/scenarios-catalog.md)。

## 开发

```powershell
python -m pytest -q
python -m build
```

项目采用 MIT License，详见 [LICENSE](LICENSE)。
API 服务可通过环境变量 `RECON_API_KEY` 或 `.reconrc` 的 `api_key` 开启鉴权；请求需携带 `X-API-Key`，调用记录写入 SQLite 审计表。
