# 性能基准

本页记录本地 Windows、Python 3.12、SSD 环境下的参考结果。实际数字会随 CPU、磁盘和数据列宽变化。

| 数据规模 | CSV 流式耗时 | CSV 峰值内存 | XLSX 流式耗时 | XLSX 峰值内存 |
|---:|---:|---:|---:|---:|
| 1,000 行 | 0.01 s | 3 MB | 0.08 s | 8 MB |
| 10,000 行 | 0.05 s | 3 MB | 0.42 s | 9 MB |
| 100,000 行 | 0.48 s | 4 MB | 4.10 s | 12 MB |

CSV 使用 `recon bench file.csv`，XLSX 使用相同命令并传入 `.xlsx` 文件。两者均逐行处理；XLSX 由 openpyxl `read_only=True` 打开，避免把全部单元格载入内存。

并行核对使用 `run_rules_parallel([...], max_workers=...)`。默认线程数为 CPU 核数的一半，规则文件之间互不共享状态。`benchmark_parallel` 同时输出串行和并行耗时，适合比较多个独立月份规则。

增量报告将文件指纹写入输出目录的 `recon_history.db`。首次发现旧的 `.manifest.json` 时自动导入 SQLite；导入后仍保留 JSON 文件作为兼容备份。SQLite 的路径主键和批量 upsert 适合上千个输入文件。

建议基准运行三次取中位数，关闭 `--progress`，并保证文件位于同一磁盘。内存值是 tracemalloc 峰值，不等于系统全部常驻内存。
