# 配置 Profile

工具内置两套可复用预设：`strict` 严格模式使用零绝对容差并关闭缺失放宽；`宽松` 模式允许 0.01 绝对容差和 0.5% 相对容差。

```powershell
python -m recon profile list
python -m recon profile show strict
python -m recon profile use 宽松 --out config/profile.json
```

`use` 会把 Profile 写成 JSON，随后可作为团队配置模板保存到项目中。Profile 是显式配置，不会隐式覆盖已有 YAML；需要将其中的 `tolerance` 和 `rules` 合并到规则文件后执行。
