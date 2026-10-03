# API 服务模式

安装依赖后可启动：

```powershell
uvicorn recon.api:app --reload
```

`POST /reconcile` 使用 multipart 上传 `file`，并以 JSON 字符串传入 `rules`；成功返回差异 JSON，文件类型错误返回 400 `INVALID_FILE`，规则或核对失败返回结构化错误。`GET /history` 读取历史快照，FastAPI 自动提供 `/docs` 交互文档。
