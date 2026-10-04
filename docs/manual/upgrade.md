# 升级与数据迁移

## 升级步骤

1. 备份项目目录、`recon_history.db`、`history/` 和自定义插件。
2. 查看当前版本：`recon --version`。
3. 拉取目标版本代码：`git pull --ff-only`。
4. 更新依赖：`pip install -r requirements.txt`。
5. 运行迁移兼容性检查：`pytest -q`。
6. 执行 `recon config show` 确认项目配置。
7. 用一份已知规则运行核对并比较报告。

## 数据迁移

新版首次打开 `recon_history.db` 时会自动创建缺失表和字段。旧版 JSON 快照可以通过 Python API 迁移：

```python
from recon.store import ResultStore

with ResultStore("recon_history.db") as store:
    print(store.migrate_json("history"))
```

迁移完成后使用 `recon history` 检查记录数量。原 JSON 文件会保留，确认数据库记录完整后再归档。

## 配置与规则兼容

- 原有 `key` 规则继续支持，多个键建议改用 `keys` 列表。
- 原有 `tolerance.default` 可继续使用；档位容差放在 `tiers` 中。
- `.reconrc` 新增字段采用默认值，不会覆盖已有规则。
- 自定义插件应保留函数签名，并在升级后运行插件测试。
- 报告模板新增字段时，旧 Excel 文件不会被原地修改，建议指定新的输出目录。

## 回滚

升级失败时停止调度任务，恢复代码和数据库备份，再运行 `pytest -q` 验证回滚版本。不要直接删除数据库；数据库包含审计、复核和调度运行记录。

## 从 v1.0.0 升级到 v1.0.1

### 变更内容
1. 新增 6 个业务场景包（多级容差、规则对比、计划编排、质量评分、通知、固定宽度工资单）。
2. 新增集成测试：三条 FastAPI 端到端链路（上传→核对→复核→报告、通知触发、增量跳过）。
3. doctor 体检新增两项：规则文件健康检查、报告输出目录可写检查。
4. 文档新增：术语表（glossary）、场景画廊索引（examples-gallery）、架构说明（architecture）。

### 升级步骤
1. 拉取最新代码：git pull origin main
2. 同步依赖：pip install -r requirements.txt
3. 运行测试确认：pytest tests/ -q（预期全部通过）
4. 历史数据无需迁移：recon_history.db 结构向后兼容，首次运行新版本时自动补齐新表。

### 注意事项
- 升级前建议备份 recon_history.db。
- 旧版规则文件无需修改，全部兼容。
- 若使用自定义插件，函数签名未变化，无需调整。
