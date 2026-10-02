# 性能基准

```powershell
python examples/generate_large.py --rows 100000
recon bench output/benchmark-100k.csv --key id
```

结果中的 `seconds`、`bytes` 和 `peak_memory_mb` 应按实际机器运行记录。
