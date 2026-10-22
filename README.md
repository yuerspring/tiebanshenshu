# 铁板神数 · V2 网页与算法对照

为传统铁板神数计算提供 Python / Flask 网页接口，展示计算步骤、原始条文和不同算法版本的差异。适合研究传统文化的程序实现；程序输出不构成对现实经历或未来事件的验证。

本仓库是 [xaminxan/tiebanshenshu](https://github.com/xaminxan/tiebanshenshu) 的 fork，网页使用 [Nanphy/TiebanshenshuOS_V2](https://github.com/Nanphy/TiebanshenshuOS_V2) 计算核心，并提供独立 OS 参考版对照。本 fork 的维护者为 [@yuerspring](https://github.com/yuerspring)。上游署名、代码及数据来源见 [来源与授权状态](THIRD_PARTY.md)。

## 功能

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

授权提示：仓库当前没有覆盖全部继承代码及数据的统一许可证。维护者确认已获相关授权，但公开授权范围仍需以权利人许可文本为准；本 README 不授予额外转载、修改或分发权利。请勿将“公开可访问”等同于已取得开源许可证。

## 深入阅读

- [API 字段与错误处理](docs/API.md)
- [V2 网页部署与已知限制](README_V2_WEB.md)
- [OS 来源、数据差异与行为说明](README_OS_COMPARISON.md)
- [上游原说明归档](docs/upstream-guide.md)（保留原作者署名；历史算法描述不代表本 fork 对准确性的承诺）
