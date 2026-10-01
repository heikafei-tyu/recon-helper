# recon-helper 对账核对工具

## 是什么
一个本地命令行工具：读取多份表格（xlsx/csv/json），按规则做跨表核对（数字对不对得上），自动找出差异并生成核对报告。

## 解决什么问题
人工核对多张 Excel 报表耗时易错（差 2 万是算错、舍入还是漏单？），本工具自动定位"哪一行哪一列、差多少、大概率什么原因"。

## 当前状态
M1 已实现读取层；M2–M5 为后续开发计划。当前不生成对账报告。

## 安装
Python 3.10+，在仓库目录执行：
```powershell
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 运行
```powershell
recon read examples/orders.xlsx
python -m recon read examples/orders-gbk.csv
python -m recon read examples/orders-utf16.csv
python -m recon read examples/orders.json
python -m pytest -q
```
读取首个 XLSX 工作表、带表头的 CSV、非空对象数组 JSON。
列名须非空且唯一，每行字段须一致。标识符保留前导零，空值统一为 null。
编码自动支持 UTF-8、GBK、带 BOM 的 UTF-16；存在歧义时用 `--encoding` 指定。
XLSX 公式会报错，须先转换为已核验的数值。类型推断仅用于摘要，不改变单元格文本。

## 运行产物
当前输出 JSON 摘要：row_count、columns、types；输入错误返回退出码 2。
examples 中所有数据为虚构示例，运行 `python examples/generate.py` 可重新生成。
后续计划依次实现 YAML 对账规则、按列容差、性能基准、Excel 报告与内容哈希增量核对。
