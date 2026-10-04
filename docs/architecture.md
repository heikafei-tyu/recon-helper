# 模块架构与数据流

```text
CLI / FastAPI
     |
  config + rules validator
     |
 readers -> Table -> engine (matcher/differ/tolerance/checks)
                         |
             severity / quality / notification
                         |
             store(SQLite) -> history / review / reports
```

## 读取层

`recon/readers/` 将 CSV、TSV、JSON、XLSX、XLS、Parquet 和固定宽度文本统一
转换为 `Table(columns, rows)`。读取器负责编码、表头、Sheet 和类型边界，之后
的核对逻辑不依赖具体文件格式。

## 核对层

`engine/core.py` 读取规则并构建左右表索引；`matcher` 负责键匹配，`differ`
负责差异结构，`tolerance` 负责绝对、相对、舍入和金额档位口径。合计、链式
勾稽、缺失期间等业务检查位于 `checks/`。

## 输出与持久化

结果先经过严重程度和质量评分，再由 Excel/HTML/CSV/JSON/PDF 导出器输出。
`ResultStore` 保存规则、输入指纹、结果和逐条复核状态；通知模块只发送摘要，
不把原始输入数据发送到外部服务。

## 服务流

FastAPI 接收上传文件和规则，临时目录执行核对，把结果写入 SQLite，返回分页
差异和历史 ID。规则编辑器和仪表盘使用 `templates/` 与 `recon/static/`，
不需要前端构建工具。
