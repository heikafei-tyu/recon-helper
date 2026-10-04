# Web 界面

启动：

```powershell
uvicorn recon.api:app --reload
```

## 规则编辑器

打开 `/web/rules`，填写左右表文件名、键列、比较列、默认绝对容差和优先级。
提交时先生成临时 YAML 并调用规则校验器；错误会回显在表单下方，校验通过
后保存到 `rules-drafts/rules.yaml`。编辑器只保存规则，不上传或执行输入文件。

编辑器使用独立的 `templates/rules_editor.html` 模板，公共样式和脚本位于
`recon/static/`，不需要前端构建工具。

## 仪表盘

打开 `/web/dashboard` 查看 SQLite 中的核对次数、累计差异数和最近十次结果。
仪表盘读取 `recon_history.db`，没有记录时显示零值；旧 JSON 快照仍可通过
历史命令读取。

仪表盘页面模板为 `templates/dashboard.html`，显示总次数、累计差异数和最近
十次结果，适合快速判断近期核对质量。

## 上传接口分页

`POST /reconcile?page=1&page_size=50` 控制响应中的差异列表页大小。完整结果
仍保存到历史库，响应包含 `total_differences`、`page` 和 `page_size`。

## 历史接口过滤

`GET /history?from_date=2026-01-01&to_date=2026-12-31&limit=50&offset=0`
按 UTC 日期过滤并分页。返回 `items` 和过滤后的 `total`，日期采用 ISO `YYYY-MM-DD`。

模板和 CSS/JS 是独立文件，修改页面布局不需要重新构建前端；API Key 鉴权和
审计中间件仍对这些页面和接口生效。
