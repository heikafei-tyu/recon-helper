# recon-helper 对账核对工具

## 是什么
一个本地命令行工具：读取多份表格（xlsx/csv/json），按规则做跨表核对（数字对不对得上），自动找出差异并生成核对报告。

## 解决什么问题
人工核对多张 Excel 报表耗时易错（差 2 万是算错、舍入还是漏单？），本工具自动定位"哪一行哪一列、差多少、大概率什么原因"。

## 安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

## 运行
recon read examples/orders.xlsx        # 查看表格摘要
recon run examples/rules.yaml          # 按规则核对，输出差异
recon bench                            # 性能基准测试
recon report --out report.xlsx         # 生成核对报告

## 运行产物
核对报告（xlsx）：差异高亮 + 汇总页（表名/行号/列/两边值/差值/疑似原因）
