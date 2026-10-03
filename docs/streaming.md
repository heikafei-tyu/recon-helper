# 流式核对

CSV 基准命令使用生成器逐行读取：

```powershell
python -m recon bench --progress
```

它生成 100000 行样例，输出行数、耗时和峰值内存。生产环境应使用 CSV 流式输入，避免把整个文件复制到内存；`--timeout` 可限制核对时长。
