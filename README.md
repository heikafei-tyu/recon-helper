# recon-helper

本地优先的财务与业务报表核对工具。读取 CSV、TSV、JSON、XLSX，按 YAML 规则定位缺失、金额差异、合计错误和跨期勾稽问题，并生成可审计报告。

## 功能特性

1. 多格式读取；2. UTF-8/GBK/UTF-16 自动识别；3. 单键和复合键；4. 按列比较；5. 绝对容差；6. 相对容差；7. 按列优先级；8. 舍入后比较；9. 数字归一化；10. 合计核对；11. 多表勾稽；12. 月日缺失检测；13. 环比同比检查；14. 多币种换算；15. 部分范围核对；16. 差异分级；17. 流式读取；18. 进度与超时；19. Excel 报告；20. HTML 报告；21. 增量指纹；22. 历史快照；23. 配置 Profile；24. 自定义插件；25. FastAPI 服务；26. 交互式向导。

## 快速开始

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
python -m recon read examples/orders.csv
python -m recon run examples/rules.yaml
python -m recon report examples/rules.yaml --out output/reconciliation.xlsx
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

## FAQ

- 中文乱码：`read --encoding gbk`。
- 找不到列：先运行 `read` 复制准确表头。
- 报告无法覆盖：关闭 Excel 或使用 `--force`。
- 大文件内存高：使用 `bench`，必要时关闭重复检查。
- 生成规则：执行 `python -m recon init`。

详见 [FAQ](docs/faq.md) 和 [故障排查](docs/troubleshooting.md)。

## 场景与安全

`examples/scenarios/` 包含应收账款、供应商、库存、报销、跨年度、预算、银行等独立业务场景，每个目录都有规则、预期结果和测试。数据默认只在本机处理；共享前请清理密钥、客户信息、内部地址和真实账号。

## 开发

```powershell
python -m pytest -q
python -m build
```

项目采用 MIT License，详见 [LICENSE](LICENSE)。
