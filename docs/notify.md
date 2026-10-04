# 核对结果通知

`recon run` 支持 Webhook 与 SMTP 两种摘要通知。Webhook 使用 JSON `POST`，
SMTP 使用纯文本邮件，摘要包含差异总数、致命数、严重数和是否通过。

```powershell
python -m recon run rules.yaml --notify-webhook https://hooks.example.test/recon
python -m recon run rules.yaml --smtp-host smtp.example.test --smtp-to ops@example.test --smtp-from recon@example.test
```

默认只有提供通知参数时发送普通通知；如果结果包含缺失数据、跨表断链等
致命差异，`force_on_fatal` 默认开启，会强制触发配置的通知通道。避免把
原始客户数据放进摘要。
