# 部署指南

## 1. 准备环境

安装 Python 3.10 或更高版本，并确认 `python --version` 正常。

## 2. 获取代码

```powershell
git clone https://github.com/heikafei-tyu/recon-helper.git
cd recon-helper
```

## 3. 创建虚拟环境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS 使用 `source .venv/bin/activate`。

## 4. 安装依赖

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
```

这会安装 CSV/XLSX/TSV、老式 XLS、Parquet、FastAPI 和报告依赖。

## 5. 验证安装

```powershell
python -m recon read examples/orders.csv
python -m pytest -q
python scripts/precheck.py
```

## 6. 运行命令行核对

```powershell
python -m recon run examples/rules.yaml
python -m recon report examples/rules.yaml --out output/reconciliation.xlsx
```

## 7. 启动 Web 服务

```powershell
uvicorn recon.api:app --host 127.0.0.1 --port 8000
```

打开 `http://127.0.0.1:8000/`。

## 8. 开启鉴权

```powershell
$env:RECON_API_KEY = "change-this-key"
uvicorn recon.api:app --host 127.0.0.1 --port 8000
```

请求时携带 `X-API-Key`。生产环境应通过安全的环境变量管理器注入密钥。

## 9. 启动调度器

```powershell
recon schedule start daily examples/rules.yaml --at 23:30
recon schedule list
recon schedule stop daily
```

调度结果和审计记录写入本地 `recon_history.db`。

## 10. 备份与升级

备份规则文件、输入数据和 `recon_history.db`。升级前运行完整测试，升级后再次执行 `scripts/precheck.py`。
