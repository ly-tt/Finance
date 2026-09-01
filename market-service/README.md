# Market Service

基于 Flask 和 AkShare 的内部行情数据服务，为 Finance 项目提供股票 K 线和基金净值数据。

## 职责边界

- 负责调用 AkShare，并将 `pandas.DataFrame` 转换为稳定的 JSON。
- 不负责用户、登录、收藏、投资组合和数据库访问。
- 当前为兼容已有 Vue 页面保留 `/api/kline` 和 `/api/fundchart`。

## 本地启动

在 PowerShell 中进入本目录：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

默认监听 `http://127.0.0.1:5000`。配置项见 `.env.example`；当前服务直接读取系统环境变量，不会自动加载 `.env` 文件。

## 接口

```http
GET /health
GET /api/kline?code=000001&start=20250101&end=20250131
GET /api/fundchart?code=110022&start=20250101&end=20250131
```

日期格式固定为 `yyyyMMdd`，查询范围最多 10 年。

## 测试

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

自动化测试使用受控的 DataFrame 替身，不依赖外部行情源是否可用。
