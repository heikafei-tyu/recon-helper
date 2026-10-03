# history 命令

## 用途

`history` 查看核对快照，追踪输入指纹、规则和结果摘要。

## 语法

```text
python -m recon history [--dir DIRECTORY]
```

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| `--dir` | 否 | 快照目录，默认 history |

## 快照内容

每次核对记录输入文件 SHA-256 指纹。

记录规则文件指纹或规则摘要。

记录执行时间和差异数量。

记录结论和错误摘要。

历史文件为 JSON，适合归档和审计。

## 示例一：默认目录

```powershell
python -m recon history
```

输出片段：

```json
{"history":[{"timestamp":"2026-10-03T10:00:00","difference_count":0}]}
```

## 示例二：指定目录

```powershell
python -m recon history --dir audit/history
```

输出片段：

```json
{"history":[{"files":["orders.csv","bank.csv"],"status":"passed"}]}
```

## 示例三：配合报告

```powershell
python -m recon report rules.yaml --out output/a.xlsx
python -m recon history
```

可据此核对报告是否对应当前输入版本。

## 示例四：空目录

```powershell
python -m recon history --dir empty-history
```

输出片段：

```json
{"history":[]}
```

## 常见错误

目录不存在时返回空列表，不代表核对已执行。

目录无读取权限时检查 Windows 文件夹权限。

损坏的 JSON 快照会报告读取错误，应从备份恢复。

不要手工修改指纹字段，否则审计关联会失效。

历史记录不包含完整客户数据，只保存摘要和路径。

使用独立目录可隔离不同项目。

定期归档旧快照以控制目录大小。

时间戳使用本机时区。

同一输入重复执行会产生多条记录。

快照不会自动上传网络。

报告增量模式依赖输入指纹。

需要清理时先备份，再删除明确的历史目录。

更多报告说明见 [report.md](report.md)。

## 对比两次记录

使用 `python -m recon history --dir history --compare 0 1` 对比按时间排序的两条记录。第一个索引是旧记录，第二个是新记录。输出 `added` 表示新增差异，`resolved` 表示已解决差异，`unchanged` 表示仍存在的差异数量。索引从 0 开始，超出范围会返回规则错误。
