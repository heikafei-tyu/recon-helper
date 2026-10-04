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
