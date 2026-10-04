# 故障排查

| 报错或现象 | 常见原因 | 处理方法 |
|---|---|---|
| `RECON_READ_ERROR` | 文件路径不存在 | 使用绝对路径或确认规则文件同目录 |
| `无法读取规则文件` | YAML 编码或缩进错误 | 保存为 UTF-8，运行 `recon validate rules.yaml` |
| `规则缺少 key` | 未配置匹配键 | 在规则中增加 `key` 或 `keys` |
| `输入缺少字段` | 表头拼写不一致 | 先执行 `recon read file.csv`，按实际表头修改规则 |
| `行主键为空或重复` | 数据未清洗 | 修复空键、重复键，或选择复合键 |
| `报告已存在` | 输出文件已存在 | 使用 `--force` 或更换 `--out` 路径 |
| Excel 无法打开 | 文件被占用或写入中断 | 关闭 Excel 后重新生成报告 |
| 中文乱码 | 编码不是 UTF-8 | 使用 `read --encoding gbk` 或 `utf-16` |
| `RECON_TIMEOUT` | 大文件执行超时 | 增大 `--timeout`，先用 `bench` 评估 |
| 内存持续增长 | 一次性加载大文件 | 使用流式读取和 `bench` 检查 |
| API 返回 401 | API Key 缺失或错误 | 设置 `RECON_API_KEY` 并传 `X-API-Key` |
| API 返回 422 | 表单字段缺失 | 对照 `/docs` 检查上传字段和规则参数 |
| 调度任务不运行 | 任务未启动或时间格式错误 | `recon schedule list`，检查 `HH:MM` |
| 调度日志为空 | 尚未到执行时间 | 使用 `--interval` 做短间隔验证 |
| 质量分过低 | 空值、类型错误或重复率高 | 查看报告 `Quality` 页签的扣分明细 |
| 通知未发送 | 开关或接收地址未配置 | 检查 webhook/SMTP 参数及网络连接 |
| 增量核对未跳过 | 文件指纹发生变化 | 确认输入文件未被重新导出或改写 |
| `ModuleNotFoundError` | 依赖未安装 | 执行 `pip install -r requirements.txt` |
| pytest 失败 | 依赖或工作目录不正确 | 在仓库根目录执行 `pytest -q` |

## 推荐定位顺序

1. 先执行 `recon read` 确认文件和表头。
2. 执行 `recon validate` 检查规则结构。
3. 用最小数据集执行 `recon run`。
4. 再生成报告并检查 `Summary`、`Differences`、`Quality` 页签。
5. 调度、API 或通知问题分别查看 `schedule logs`、API 响应和运行日志。
