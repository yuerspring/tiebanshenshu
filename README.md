# 铁板神数 · 视频演算

只保留泽方[视频中的计算流程](https://www.youtube.com/watch?v=o3mkGBcPkrI)：太玄考刻、父母流度候选、四柱取数、基数化卦、前后卦及大运未合化分支。

打开页面，填写出生日期或四柱；点击“视频例子”可直接运行教学案例。条文使用现有对照库，条文版本差异不阻断数值计算。

## 运行

```sh
python -m pip install -r requirements.txt
python webui.py
```

访问 http://localhost:7860 。生产部署使用仓库的 Dockerfile，监听环境变量 PORT，健康检查 `/api/v1/health`。

## 验证

```sh
python -m unittest discover -s tests -v
python scripts/audit_data.py
```

教学四柱乙巳、辛巳、甲申、丙子；所选演算基数9003，运柱壬午。太玄和55，考刻候选9467，八卦加则2381/4381/6382/8389，大运示例6476。

[完整演算链](docs/VIDEO_CHAIN_REPLAY.md)区分视频明写的答案与按上下文推导的结果；[画面配数表](docs/VIDEO_INSERT_TABLES.md)记录出处。后天中五寄卦、未演示的合化条件只暂停对应分支。

## 项目结构

- `webui.py`：页面、视频计算接口、健康检查。
- `tiebanshenshu/methods/`：视频规则、配数表、互卦及条文读取。
- `tiebanshenshu/calendar.py`：日期换算；按当地民用时间，23点换日。
- `templates/`、`static/`：唯一页面及样式。
- `DB/List.csv`：条文对照库。
- `tests/`：视频算例、接口、删除旧功能和命令行回归。

唯一计算接口为 `POST /api/v1/video-chart`，输入可包含 `bazi` 或 `birth_date`/`birth_time`，以及可选的 `known_parents`、`basis_number`、`fortune_pillar`。

```json
{"bazi":{"year":"乙巳","month":"辛巳","day":"甲申","time":"丙子"},"basis_number":9003,"fortune_pillar":"壬午"}
```

本次已删除十四表引擎、历史入口、OS对照、时刻敏感性工具和专用数据，旧版本可从Git历史查看。来源见[THIRD_PARTY.md](THIRD_PARTY.md)。程序复算不等于现实预测获得验证。

## 授权与致谢

本项目由宇正伟担任主要维护者。感谢原作者 [xaminxan](https://github.com/xaminxan) 授权本项目公开维护、修改和分发。
