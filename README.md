# 铁板神数 · 视频演算与算法对照

为传统铁板神数计算提供 Python / Flask 网页接口，展示计算步骤、原始条文和不同算法版本的差异。适合研究传统文化的程序实现；程序输出不构成对现实经历或未来事件的验证。

本仓库是 [xaminxan/tiebanshenshu](https://github.com/xaminxan/tiebanshenshu) 的 fork，历史版网页使用 [Nanphy/TiebanshenshuOS_V2](https://github.com/Nanphy/TiebanshenshuOS_V2) 计算核心，并提供独立 OS 参考版对照。本 fork 的维护者为 [@yuerspring](https://github.com/yuerspring)。上游署名、代码及数据来源见 [来源与授权状态](THIRD_PARTY.md)。

## 功能

- 首页按泽方公开视频分步复算：太玄候选、八卦加则、干支化数，附来源时间和条文版本差异。
- 未完成依据的步骤保持待核；十四表本命、流年和OS对照保留在 `/legacy`。

- 手机与桌面浏览器可用的中文输入与结果页。
- 本命条文、逐项计算过程和 1～108 岁流年字段。
- 可选六亲生肖核对；明确展示该信息是否影响本命条文。
- 同一小时四个 15 分钟段的敏感性比较。
- V2 与归档 OS 算法、数据表的独立对照。
- JSON API、Docker 部署与自动回归测试。

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

测试覆盖正常输入、晚子时、生肖核对、108 岁结果、四段比较、OS 对照、错误输入、请求大小和健康检查。OS 对照自动读取共享 CSV，无需建立软链接。算法一致性测试只证明程序行为一致，不能证明传统命理判断的现实准确性。

## API 示例

```sh
curl -X POST http://localhost:7860/api/v1/chart \
  -H 'Content-Type: application/json' \
  -d '{"gender":"男","birth_date":"1924-06-15","birth_time":"16:00","query_date":"2025-04-20","query_time":"10:00","known_shengxiao":{}}'
```

字段与错误格式见 [API 文档](docs/API.md)。该示例当前计算的本命数为 **344**；与旧版说明中的 345 不同，原因见 [V2 网页说明](README_V2_WEB.md)。

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
