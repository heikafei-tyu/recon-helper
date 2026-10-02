# Quickstart

## 1. 创建环境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 2. 运行示例

```powershell
python examples/generate.py
python -m recon read examples/orders.xlsx
python -m recon validate examples/rules.yaml
python -m recon run examples/rules.yaml
python -m recon report examples/rules.yaml --out output/reconciliation.xlsx
```

## 3. 验证安装

```powershell
python -m pytest -q
python -m build
```

输入文件只在本机读取。示例数据是虚构数据；生产文件不要提交到 Git。
