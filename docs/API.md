# JSON API

## 请求

`POST /api/v1/chart` 返回 V2 排盘；`POST /api/calculate` 为兼容路径。`POST /api/v1/time-sensitivity` 比较出生小时内四段，`POST /api/v1/compare-os` 独立计算 OS 对照。四个路径使用同一请求结构：

```json
{
  "gender": "男",
  "birth_date": "1924-06-15",
  "birth_time": "16:00",
  "query_date": "2025-04-20",
  "query_time": "10:00",
  "known_shengxiao": {"父亲": "鼠"}
}
```

| 字段 | 约束 |
| --- | --- |
| `gender` | 必填，`男` 或 `女` |
| `birth_date`, `query_date` | 必填，有效公历日期，严格使用 `YYYY-MM-DD` |
| `birth_time`, `query_time` | 必填，24 小时 `HH:MM`，不包含秒、时区或 UTC 偏移 |
| `known_shengxiao` | 可省略；提供时必须为对象，不能为 `null`、数组或字符串 |
| 生肖对象的键 | 仅 `父亲`、`母亲`、`兄弟`、`配偶`、`子女` |
| 生肖对象的值 | `鼠牛虎兔龙蛇马羊猴鸡狗猪` 中的一个字 |

输入出生时间不能晚于求测时间。出生 23 点按次日 00 点同分处理；求测时间保持输入值。网页出生日期选择范围为 1900～2099，超出历法库支持范围的 API 输入可能返回转换错误；不声称对任意年代有效。输入按当地民用时间直接使用，调用方负责时区、夏令时及历史时间换算。

请求应使用 `Content-Type: application/json`，正文上限 4096 字节。无 `Content-Length` 的流式请求在支持该标记的 WSGI 服务器中也受读取限制，截断 JSON 可能返回 400，而非 413。部署者仍需在代理层限制请求体、并发与调用频率。

## 响应

成功：HTTP 200，`{"success": true, "data": {...}}`。`chart` 的 `data` 包含输入、八字信息、`destiny_articles`、完整 `result` 和 `validation`；`result.liunian` 包含 108 个年龄结果。`validation` 额外返回所有已用六亲、候选列表、候选状态和未支持条件；`source_status=unverified` 不代表已完成古籍验条。其余接口的字段与解释分别见 `README_V2_WEB.md`、`README_OS_COMPARISON.md`。

失败：`{"success": false, "error": {"code": "INVALID_INPUT", "message": "…"}}`。

| HTTP | code | 含义 |
| --- | --- | --- |
| 400 | `INVALID_INPUT` | JSON 结构、性别或生肖不合法 |
| 400 | `INVALID_DATETIME` | 日期时间缺失、格式错误、转换失败或先后顺序错误 |
| 413 | `INVALID_INPUT` | 请求超过大小限制 |
| 500 | `CALCULATION_FAILED` | 未预期的计算错误，客户端不接收堆栈信息 |

API 响应使用 `Cache-Control: no-store`。不要把真实生日等个人资料放入 URL、公开 issue 或调试日志。

## 就绪检查

`GET /api/v1/health` 返回 `success`、`engine`、`database_loaded`。断语映射已加载时为 200，映射为空或初始化失败时为 503。它是基础就绪信号，不证明全部算法结果或每个 CSV 都正确。
