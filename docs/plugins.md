# 自定义规则插件

插件放在项目根目录 `plugins/`，约定导出：

```python
def check(left, right, rule):
    return [{"status": "plugin_mismatch"}]
```

使用 API 发现和执行：

```python
from recon.plugins import discover_plugins, run_plugin
print(discover_plugins())
run_plugin("amount_range", [10], [12], {"limit": 1})
```

插件必须返回列表；函数签名不是三个参数、插件不存在或返回其他类型都会报错。插件运行在当前 Python 进程中，应只处理可信代码，不要从外部输入直接执行任意脚本。
