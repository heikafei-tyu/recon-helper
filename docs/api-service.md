# API 服务模式

安装依赖后可启动：

```powershell
uvicorn recon.api:app --reload
```

`POST /reconcile` 使用 multipart 上传 `file`，并以 JSON 字符串传入 `rules`；成功返回差异 JSON，文件类型错误返回 400 `INVALID_FILE`，规则或核对失败返回结构化错误。`GET /history` 读取历史快照，FastAPI 自动提供 `/docs` 交互文档。

配置 `RECON_API_KEY` 环境变量或 `.reconrc` 的 `api_key` 后，所有请求必须携带 `X-API-Key`，否则返回 401。每次请求的时间、调用者摘要、方法、路径和状态码写入 SQLite `audit_log` 表。

## Web 页面与持久化

打开根路径 `/` 可上传左右表和 YAML 规则，结果表按致命、严重、提示显示颜色。`/web/history` 展示本地历史核对，`/web/reports` 提供报告命令入口。每次 API 核对写入 `recon_history.db` 的 `results` 和 `diffs` 表；查询可按 `table_name`、`severity` 和数量限制过滤。旧 `history/*.json` 可用 `ResultStore.migrate_json` 导入，命令行历史在数据库不存在时继续读取 JSON。
