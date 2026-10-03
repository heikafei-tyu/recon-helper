# 故障排查

1. 先运行 `python -m recon validate rules.yaml`，一次查看规则结构错误。
2. 遇到 `RECON_READ_ERROR`，确认编码、表头唯一性、CSV 每行列数和 XLSX Sheet 名称。
3. 遇到 `RECON_TIMEOUT`，先用 `recon bench --progress` 测量文件规模，再增加超时或改用流式 CSV。
4. 报告已有文件时使用 `--incremental` 或 `--force`，不要直接覆盖历史结果。
5. 运行测试使用 `python -m pytest -q`；格式检查使用 `ruff check recon tests`。
