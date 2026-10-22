# 铁板神数 V2 网页部署

本网页将 `Nanphy/TiebanshenshuOS_V2` 的 `main.TieBanCalculator.calculate()` 封装为 JSON API，保留十四表本命/流年规则及 DB 原文；考刻候选模块已修复无匹配强选第一刻和只读首个六亲的问题。旧十进制生肖规则尚未完成古籍验条，狗/猪对应地支超出其表示范围，明确标记为不支持而不伪造候选。输入支持男/女、公历出生与求测时间，以及可选的父亲、母亲、兄弟、配偶、子女生肖考刻验证。响应完整保留 `result` 下的 108 岁流年和 V2 的全部 `keke` 扩展字段，前端可逐项展开。

运行：`pip install -r requirements.txt && gunicorn -w 2 -b 0.0.0.0:8000 webui:app`。健康检查为 `GET /api/v1/health`；排盘为 `POST /api/v1/chart`，请求示例：

```json
{"gender":"男","birth_date":"1924-06-15","birth_time":"16:00","query_date":"2025-04-20","query_time":"10:00","known_shengxiao":{}}
```

Docker：`docker build -t tiebanshenshu-v2 . && docker run -p 8000:8000 tiebanshenshu-v2`。Render 读取 `render.yaml`，使用 `$PORT`。出生信息仅用于当前请求的计算，服务不会写入数据库。

验证时要区分 **程序一致性** 与 **现实准确性**：前者可以和同一仓库的命令行算法逐字段对照；后者需要以已知事实核对，程序生成的六亲条文不能自动视为事实。上游 README 中 1924-06-15 示例写作农历五月十五及本命数 345，但当前代码实际运行转换为五月十四、本命数 344；以实际运行代码为网页依据。若用户已知兄弟人数与条文不符，页面保留原条文号和公式，不私自改写 V2 数据。


## 考刻候选状态

全部已填六亲同时参与数值候选核对。`validation.status` 为 `not_provided`、`no_match`、`unsupported`、`ambiguous` 或 `unique_candidate`；只有一个共同候选且没有不支持条件时，`k_true` 才为整数，否则为空。`source_status=unverified` 表示尚未完成古籍规则核验，候选不代表命理事实已验证。每刻记录各六亲匹配、冲突和未评估条件；查到一个条文号也不会把 `text_verified` 改为真。
