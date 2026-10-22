# 来源与授权状态

本文件记录来源，不代替各权利人的许可证，也不为继承材料重新授权。

| 材料 | 来源 | 本仓库处理 |
| --- | --- | --- |
| 原始 fork 与历史说明 | [xaminxan/tiebanshenshu](https://github.com/xaminxan/tiebanshenshu) | 保留作者署名，历史 README 完整归档于 `docs/upstream-guide.md` |
| V2 计算核心及数据 | [Nanphy/TiebanshenshuOS_V2](https://github.com/Nanphy/TiebanshenshuOS_V2) | 沿用计算规则；网页封装与测试单独维护，见 `README_V2_WEB.md` |
| OS 对照实现 | [Nanphy/TiebanshenshuOS](https://github.com/Nanphy/TiebanshenshuOS/tree/785dc871d523e1c4d7772946955fd30fc8ebb4bf) | 归档代码位于 `reference_os/main.py`，禁用本地调试上报钩子，数据差异见 `README_OS_COMPARISON.md` |
| 第三方 Python 依赖 | `requirements.txt` 中列出的发行包 | 按各依赖自身的许可证使用，不受本仓库说明替代 |

维护者确认拥有相关使用和维护授权。当前仓库未附覆盖所有继承代码和 CSV 数据的公开许可文本，不能据此推定对所有人的修改或再分发许可。若希望转载、分发、商用或提交含第三方材料的改动，请先确认对应权利人的授权范围。

待维护者与权利人核对后，应补充可公开的许可文本、适用文件范围和归属信息；不要直接给整仓库套用 MIT 等许可证。现有作者署名和来源记录不得因申请资助或展示项目而删除。

## 公开视频规则依据

新增 `methods/video.py` 与 `video_tables.py` 根据维护者提供的泽方公开视频 [o3mkGBcPkrI](https://www.youtube.com/watch?v=o3mkGBcPkrI) 重新实现公开计算步骤。未复制完整视频、完整转写或截图到仓库，也不把 xaminxan 的授权扩大到该视频。逐项来源和限制见 [视频核验](docs/VIDEO_VERIFICATION.md)。
