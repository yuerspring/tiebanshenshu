# JSON API

## 视频公开步骤

默认使用 `POST /api/v1/chart`；`POST /api/calculate` 和 `POST /api/v1/video-chart` 均调用同一视频流程，不再返回旧十四表排盘。教学示例：

```json
{"bazi":{"year":"乙巳","month":"辛巳","day":"甲申","time":"丙子"},"fortune_pillar":"壬午"}
```

也可省略`bazi`而提供`birth_date`、`birth_time`，沿用现有日期转换，结果标记`legacy_calendar_conversion_not_video_verified`。视频没有验证该历法实现。

可选`confirmed_number`必须为1001–9999的整数，并同时提供`number_confirmed: true`，表示调用者根据事实核验，不是接口自动选定；`benming_gua_number`为1–13000的整数，独立表示有出处的本命卦数，不自动从考刻条号推断。`fortune_pillar`只复算未合化分支，不能据此推算大运起岁。

返回`preliminary`、`pillar_articles`、`number_method`、`before_after`、`annual`与`edition_conflicts`。`source_seconds`为视频出处。未知条件返回明确状态和空候选结论；共享条文的`fact_verified`默认为false。格式错误返回HTTP400 `INVALID_INPUT`，请求限制与下文相同。规则范围见[视频核验](VIDEO_VERIFICATION.md)。

可选 `known_parents` 示例：`{"父亲":"鼠","母亲":"牛"}`。仅接受父亲、母亲与十二生肖，返回 `parent_candidates`（固定流度基条及加10的五项候选）。这些候选不自动标记为已核验。

`life_sequence` 仅在明确确认的四位基数成功生成论命基数后返回：逐加96，超过13000减12000，回到起点停止；不自动判断寿终。现有 List.csv 的所有条文都标记 `corpus_role: comparison_only`、`video_edition_verified: false`。4381的文字与视频22:30画面一致时另标记`video_text_verified: true`，并附取证时间；不扩大为整库版本确认。

## 历史十四表请求

`POST /api/v1/legacy/chart` 返回 V2 排盘；`POST /api/legacy/calculate` 为兼容路径。`POST /api/v1/legacy/time-sensitivity` 比较出生小时内四段，`POST /api/v1/legacy/compare-os` 独立计算 OS 对照。四个路径使用同一请求结构：

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


## 完整时辰敏感性

`POST /api/v1/legacy/time-audit`：同排盘请求加可选 `resolution_minutes`（只能为整数 1 或 15，不接受布尔值）。返回 `window_start`、`window_end_exclusive`、`samples` 和 `summary`。默认 8 样本；逐分钟模式为 120 样本，计算量更大，部署者应设置访问频率和并发限制。采样窗口必须不晚于求测时间。该工具展示既有规则的敏感性，不推定哪个出生分钟真实。

排盘响应 `time_basis` 保留历法换日时间与钟表初定刻坐标，`timezone_conversion=false` 表示未执行时区/太阳时换算。23:05 与次日 00:05 可能沿用相同历法输入，但原钟表八刻分别为 1、5；不要把这两个概念混为一谈。


## 数据来源与缺项

`result.hexagram_source` 记录表名、刻别、本命数、是否找到和是否回退。当前不允许用其他刻别填补缺项。`result.data_warnings` 出现 `MISSING_HEXAGRAM_ENTRY` 时，本命条文为空，页面会提示；不要把缺项当成预测结论。HTTP 200 表示请求已完成，不表示每个数据库字段都完整或具有古籍权威。

### 书页依据和校正候选

图表响应新增 `method_basis`，说明十四表初刻／正刻的规则来源、核验范围以及出生分钟不直接进入本命公式。流年行保留兼容字段 `corrected_fortune` 等，但它们仅为旧规则自动生成的候选；新增 `correction_status: unverified_candidate`、`correction_applied: false`。消费者应默认展示 `original_fortune` 和 `original_duanyu`，不得把候选标为已经事实验证。具体见 `BOOK_VERIFICATION.md`。

## 叠加表核对

`reference_tables` 返回视频叠加的8张数表及出处时间；`source_conflicts` 明确记录流年排列文字卡与白板算例冲突。详见[视频插表核对](VIDEO_INSERT_TABLES.md)。
