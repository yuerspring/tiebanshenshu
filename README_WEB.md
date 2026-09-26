# 铁板神数 Web

原始命盘计算与 CSV 解析仍由仓库根目录 `main.py` 中的 `TieBanCalculator`、`TieBanDataLoader` 执行。Web 代码负责时间输入、API、JSON 映射与浏览器显示；数据库仍是 `数据库/` 下的原文件。`main.py` 适配了 `14-10.csv` 的实际列名、单元格内换行的多个偏移量，以及相对脚本的数据库路径和可注入的共享 loader。原公式未改动。

## 本地启动

建议 Python 3.12：

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m uvicorn app.server:app --host 0.0.0.0 --port 8000
```

打开 `http://localhost:8000`。生产环境设 `PORT`，启动命令：

```sh
uvicorn app.server:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers
```

## Docker

```sh
docker build -t tiebanshenshu .
docker run --rm -p 8000:8000 tiebanshenshu
```

Render 可从 `render.yaml` 创建 Docker Web 服务，或在 Railway/Fly.io 选择 Dockerfile 部署；健康检查 `/api/v1/health`，无需数据库服务。VPS 用 Docker 运行，生产公网建议在反向代理上提供 HTTPS、连接数和请求超时限制。部署前自行设置域名：仓库不绑定特定域名，也不会自动使用第三方平台提供的子域名。

## API

`POST /api/v1/chart`，`Content-Type: application/json`：

```json
{"gender":"男","birth_datetime":"1924-06-15 16:00","query_datetime":"2025-04-20 10:00"}
```

返回 `{ "success": true, "data": { "basic_info": {}, "basic_chart": {}, "destiny_articles": [], "annual_fortunes": [], "destiny_source": null, "original_fields": {} } }`。`annual_fortunes` 只筛出原计算中的 1～100 岁；`original_fields.liunian` 原样保留 1～108 岁，以方便与原程序内部结果逐字段比较。`destiny_articles` 为原 `tbl_data` 的结构化呈现，断语从原条文断词表查询；找不到时列表为空。

`POST /api/v1/report.md` 使用同一 JSON 请求体，直接返回 Markdown 下载，不在服务器上保存出生信息或报告。

`GET /api/v1/health` 是启动和数据库可用性检查。`GET /`、`GET /result` 为移动端排盘页面，`GET /about` 为说明页。

错误格式：`{"success":false,"error":{"code":"INVALID_DATETIME","message":"出生时间不能晚于求测时间"}}`。无用户可控的 CSV 或输出路径。默认每 IP 每分钟 20 次，仅在服务进程内计数；公开部署可在代理层增设统一限流。`CORS_ORIGINS` 留空表示没有跨域开放；需要分离前端时可设逗号分隔的可信来源。

## 回归

`python -m pytest -q`。`tests/baselines/before_14_10_fix/` 保留三组修复前 CLI 完整输出；`tests/baselines/` 保存三组表头适配后 CLI 的完整输出及 Markdown，README 样例为第一组。测试将 Web Markdown 全文与适配后的 CLI 对比（排盘时间一项固定为基线时刻），并确认核心命数与 100 岁流年同修复前逐列一致。晚子时输入也测试。原仓库 README 的排盘时间是过去生成的示例值，因此每次即时运行的时间戳不同。

原 `main.py` 的 `save_to_md()` 中本命条文只写数字及公式；本 Web JSON 在此基础上查询同一条文断词 CSV，展示匹配断语。找不到的条文保持缺失。部分晚年在原项目数据表没有匹配，原计算结果为空，网页亦不补造数据。

**已修复的原仓库兼容问题：**`14-10.csv` 实际列名为 `十二辟卦`、`初刻生人先天命数`、`正刻生人先天命数`，旧 `main.py` 加载器读取了不存在的列名，导致所有本命条文缺失。现仅对表头及单元格内的换行进行解析适配：144 行 CSV 可分别对应初刻和正刻，加载出 288 项映射。README 样例现有四条本命条文；对照修复前基线，核心命数与 100 岁流年均未变化。
