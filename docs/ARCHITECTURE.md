# 代码结构与维护入口

项目把计算、数据、静态表和输出分开。根目录入口保留兼容性，新增功能应直接在 `tiebanshenshu` 包对应模块修改，避免重新堆入主文件。

```text
tiebanshenshu/
├── __main__.py           # python -m tiebanshenshu
├── calendar.py           # 农历和四柱转换
├── paths.py              # 数据资源绝对路径
├── data/
│   ├── csv_reader.py     # CsvTableReader：编码兼容、单元格清洗
│   └── loader.py         # TieBanDataLoader：按表类型分别加载
├── engine/
│   ├── calculator.py     # TieBanCalculator：本命及整体流程
│   ├── annual.py         # AnnualCalculator：十四表流年
│   └── extensions.py     # ExtensionCalculator：组合扩展结果
├── kaoke/
│   ├── candidates.py     # 八刻候选筛选、验条号
│   ├── relationships.py  # 纳音、刑合空等共用判断
│   ├── relatives.py      # 父母、兄弟、子女、配偶
│   ├── palaces.py        # 命宫、六亲宫位、卦气转换
│   ├── family.py         # 婚姻及家庭扩展
│   ├── hexagrams.py      # 起卦、互卦、变卦
│   ├── numbers.py        # 基础配数、起宿、事项条号
│   ├── bagua.py          # 八卦滚心、快速断命
│   ├── derived.py        # 河洛、音韵与六亲秘法
│   ├── annual.py         # 百岁配数等扩展流年
│   └── orchestrator.py   # 组合考刻模块
├── tables/               # 按领域保存静态表，无文件读取
└── presentation/
    ├── cli.py            # 用户输入、命令行调度
    └── reports.py        # ReportWriter：终端和Markdown报告

main.py                   # 简短兼容入口
keke_module.py            # 原函数/常量导入兼容层，不保存第二份实现
webui.py                  # Flask接口、请求校验、网页响应
DB/                       # 现有CSV语料与查表数据
reference_os/             # 独立历史参考实现，保留原貌
```

## 如何定位修改

| 维护事项 | 修改位置 |
|---|---|
| CSV读取失败、编码或字段识别 | `data/csv_reader.py`、`data/loader.py` |
| 本命公式与初刻／正刻 | `engine/calculator.py` |
| 十四表流年与校正候选 | `engine/annual.py` |
| 六亲条件冲突、无匹配或多候选 | `kaoke/candidates.py` |
| 父母／兄弟／子女／配偶算法 | `kaoke/relatives.py` |
| 增加扩展算法的结果 | 对应 `kaoke` 模块，再由 `engine/extensions.py` 组合 |
| 报告排版 | `presentation/reports.py` |
| 接口字段与错误处理 | `webui.py` |

`TieBanDataLoader._load_all()` 只负责顺序调度，具体分成基础表、卦象、本命、流年规则、流年条文、语料、秘数与姓名数据的加载方法。纯算法继续使用函数；需要持有数据库或组合流程的组件使用类。

依赖方向是：接口/命令行 → 计算服务 → 领域算法和数据。静态表不依赖算法，算法不导入兼容入口。避免跨模块通配符导入和运行时注入全局变量。历史重复定义的配数表保留最终生效的值，已逐项对照82张表及14个六亲公式。

## 启动与兼容

原 `python main.py` 和 `gunicorn webui:app` 不变，也可 `python -m tiebanshenshu`。旧 `from main import TieBanCalculator`、`from keke_module import kao_ke` 引用的是新包中的同一个对象。

Docker镜像必须包含 `tiebanshenshu/`；Dockerfile已增加复制步骤。`DB` 路径相对项目资源目录定位，切换工作目录不影响加载。

## 拆分验证

除书页算例和接口测试外，增加了包模块导入、兼容对象、异目录数据加载及异目录命令行报告测试。拆分前后使用8组虚构输入（含普通时刻、晚子时、闰日、生肖条件、狗猪不支持条件），完整JSON响应逐字一致；这证明本轮结构迁移未改变这些样本的既有行为，不等于全部算法经过古籍验证。
