"""Markdown text follows original save_to_md's field order, without disk writes."""
from datetime import datetime


def render_markdown(data, generated_at=None):
    res = data["original_fields"]
    generated_at = generated_at or datetime.now()
    lines = [
        "# 铁板神数排盘结果", "",
        f"**排盘时间**: {generated_at:%Y-%m-%d %H:%M:%S}", "",
        "## 基础信息", "```", res["header_info"], "```", "",
        "## 基础排盘",
        f"- 先天命数：{res['cong_calc']}",
        f"- 五音命数：{res['tone_num']}",
        f"- 日命数 & 时运数：{res['day_life_calc']}",
        f"- 考刻结果：{res['moment_calc']}",
        f"- 本命数：{res['main_calc']}",
        f"- 十二辟卦：{res['hex_name']}", "",
        "## 本命条文",
    ]
    if res["tbl_data"]:
        tbl = res["tbl_data"]
        base, seq, offsets = tbl["base"], tbl["seq"], tbl["offsets"]
        lines.extend([
            f"**{res['moment_cn']}生人 - 先天命数 {res['cong_num']} - {res['hex_name']}(+{base})**", "",
            "| 项目 | 数值 | 计算公式 |", "|------|------|----------|",
            f"| 序数 | {seq} | - |",
        ])
        for item, values in offsets.items():
            for value in values:
                total = base + seq + value
                lines.append(f"| {item} | {total} | {base} + {seq} + {value} = {total} |")
    else:
        lines.extend(["未找到匹配的本命条文数据", ""])
    lines.extend([
        "## 流年条文 (1-100岁)",
        "| 岁数 | 干支 | 四声 | 标记 | 字母 | 校正数 | 校正后校正数 | 计算公式 | 原条文 | 原断语 | 原断语年龄 | 校正后条文 | 校正后断语 | 校正后断语年龄 |",
        "|------|------|------|------|------|--------|--------------|----------|--------|--------|------------|------------|------------|----------------|",
    ])
    for i in data["annual_fortunes"]:
        original = i["original_duanyu"].replace("|", "｜").replace("\n", " ")
        corrected = i["corrected_duanyu"].replace("|", "｜").replace("\n", " ")
        lines.append(
            f"| {i['age']} | {i['year']} | {i['sound']} | {i['marker']} | {i['letter']} | "
            f"{i['original_correction']} | {i['corrected_correction']} | {i['formula']} | "
            f"{i['original_fortune']} | {original} | {i['original_duanyu_age']} | "
            f"{i['corrected_fortune']} | {corrected} | {i['corrected_duanyu_age']} |"
        )
    return "\n".join(lines) + "\n"
