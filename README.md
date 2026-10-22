# 铁板神数 · 视频演算与算法对照

为传统铁板神数计算提供 Python / Flask 网页接口，展示计算步骤、原始条文和不同算法版本的差异。适合研究传统文化的程序实现；程序输出不构成对现实经历或未来事件的验证。

本仓库是 [xaminxan/tiebanshenshu](https://github.com/xaminxan/tiebanshenshu) 的 fork，历史版网页使用 [Nanphy/TiebanshenshuOS_V2](https://github.com/Nanphy/TiebanshenshuOS_V2) 计算核心，并提供独立 OS 参考版对照。本 fork 的维护者为 [@yuerspring](https://github.com/yuerspring)。上游署名、代码及数据来源见 [来源与授权状态](THIRD_PARTY.md)。

## 功能

- 默认网页、JSON 排盘接口和命令行统一走泽方视频的推导流程。
- 可展开查阅视频中叠加的8张配数表，附原视频时间与文字卡/白板冲突记录。
- 独立视频模块提供太玄初候选、月上年下考刻、八卦加则、干支化数、父母生肖流度基条和逐加10核对候选。
- 所选的四位基数可以直接继续演算，是否经过现实事实核验另行记录；基数化卦后自动接续前后卦，并生成逐加96、超过13000减12000、回到起点停止的论命条号序列。
- 条文库仅作版本对照，不冒充视频底本；不会从生肖直接选中真实刻分。
- 教学案例可一键连续复算；后卦中五寄卦、未演示的合化条件只暂停对应分支。当前不会自动声称验得真实出生刻分。
- 旧十四表退出默认入口，仅保留显式历史接口和源码用于复核，不参与视频计算。

先看[视频例子连续复算](docs/VIDEO_CHAIN_REPLAY.md)。

视频和《皇极经世书》的核对结果、已发现的条号差异，见 [视频方法迁移记录](docs/VIDEO_ONLY_MIGRATION.md)。

命令行复算视频教学四柱：

```sh
python -m tiebanshenshu --pillars 乙巳 辛巳 甲申 丙子 --basis-number 9003 --fortune-pillar 壬午 --output output/video.json
```

## 本地启动

建议使用 Python 3.12，与 Docker 镜像一致。在仓库根目录执行：

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python webui.py
```

打开 http://localhost:7860 。退出使用 Ctrl+C。Windows 可用 `.venv\Scripts\activate` 激活环境。无需 API key、OpenAI 账户或外部推理服务。系统按输入的当地民用时间直接计算，不自动转换时区或夏令时。

## 运行测试

```sh
python -m unittest discover -s tests -v
```

运行 `python scripts/audit_data.py` 可核对 CSV 快照和条文完整性。审计同时列出已知的正刻 700 缺项及正刻 670 重复，不能把快照一致等同于表格已校勘无误。

测试覆盖视频样例、父母流度、96轮转、新入口隔离、错误输入、请求大小、健康检查，以及历史算法回归。OS 对照自动读取共享 CSV，无需建立软链接。算法一致性测试只证明程序行为一致，不能证明传统命理判断的现实准确性。

## API 示例

```sh
curl -X POST http://localhost:7860/api/v1/chart \
  -H 'Content-Type: application/json' \
  -d '{"bazi":{"year":"乙巳","month":"辛巳","day":"甲申","time":"丙子"},"known_parents":{"父亲":"鼠","母亲":"牛"}}'
```

字段与错误格式见 [API 文档](docs/API.md)。教学示例太玄合计55、第二种考刻候选9467、四柱八卦加则数2381/4381/6382/8389，均附步骤；不自动确定真刻。

## 部署

```sh
docker build -t tiebanshenshu .
docker run --rm -p 8000:8000 tiebanshenshu
```

健康检查：`GET /api/v1/health`。断语数据未载入时返回 HTTP 503。`render.yaml` 提供现有 Render 配置；生产环境应在入口设置访问频率限制和请求超时。服务无需出生信息数据库，不会把网页请求写入排盘报告；API 响应标记 `Cache-Control: no-store`。浏览器中的结果、手动复制内容，以及托管平台日志仍由使用者和部署者管理。

## 维护与贡献

欢迎可复现的错误报告、文档改进和带测试的修复。请先阅读 [贡献指南](CONTRIBUTING.md) 与 [安全报告说明](SECURITY.md)，勿上传真实个人或亲属出生资料。维护记录见 [CHANGELOG](CHANGELOG.md)，后续工作见 [维护计划](docs/ROADMAP.md)。

代码、数据及参考实现的来源和许可信息见 [来源说明](THIRD_PARTY.md)。

## 代码结构

主程序已按数据加载、本命／流年服务、考刻领域算法、静态表和报告输出拆分为 `tiebanshenshu/` 包。根目录保留兼容入口；修改位置和启动方法见[结构与维护指南](docs/ARCHITECTURE.md)。

## 深入阅读

- [算法、古籍与网站对照核查](docs/ALGORITHM_AUDIT.md)
- [API 字段与错误处理](docs/API.md)
- [V2 网页部署与已知限制](README_V2_WEB.md)
- [OS 来源、数据差异与行为说明](README_OS_COMPARISON.md)
- [上游原说明归档](docs/upstream-guide.md)（保留原作者署名；历史算法描述不代表本 fork 对准确性的承诺）


## 书页核验进展

已按用户提供PDF的实际内页核对初刻／正刻规则与选定算例，修复一处会改变流年条号的“神→福”录入差异。流年默认显示原始条文，自动加数只作未核实候选；未提供逐分钟推命规则。文件名与内页标题不一致，完整范围、页码和未核项见[书页核验记录](docs/BOOK_VERIFICATION.md)。

### 新增书籍核验记录

徐宇辳本与金泉本的规则、案例、版本差异及未核验范围见 [两书定点核验](docs/BOOK_COMPARISON.md)。

### 视频公开步骤复核

首页现在按泽方公开视频提供分步复算，原十四表界面保留在 `/legacy`。已支持太玄候选、八卦加则、干支化数和部分已核验数推演；条文底本冲突与缺失规则不会自动填默认。详见 [视频音画核验与实现边界](docs/VIDEO_VERIFICATION.md)。

## 授权与致谢

本项目由宇正伟担任主要维护者。感谢原作者 [xaminxan](https://github.com/xaminxan) 授权本项目公开维护、修改和分发。
