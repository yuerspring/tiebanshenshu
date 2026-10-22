"""终端与Markdown报告输出；不参与计算。"""
import datetime
import os


class ReportWriter:
    def print_report(self, res):
        print("\n" + "="*220)
        print(res['header_info'])
        print("="*220 + "\n")

        print("【基础排盘信息】")
        print(f"{res['cong_calc']}")
        print(f"五音命数 = {res['tone_num']}")
        print(f"{res['day_life_calc']}")
        print(f"{res['moment_calc']}")
        print(f"{res['main_calc']}")
        print(f"十二辟卦: {res['hex_name']}")

        print("\n【本命条文】")
        if res['tbl_data']:
            tbl = res['tbl_data']
            base, seq, offsets = tbl['base'], tbl['seq'], tbl['offsets']
            print(f"十二辟卦 —— {res['hex_name']}  +{base}")
            print(f"{res['moment_cn']}生人  先天命数 {res['cong_num']}")
            print("-" * 60)
            print(f"{'序数':<6}{'性格':<10}{'才能前程':<10}{'财运':<10}{'兄弟个数':<10}")
            s_char = ",".join(map(str, offsets['性格']))
            s_car = ",".join(map(str, offsets['才能前程']))
            s_wea = ",".join(map(str, offsets['财运']))
            s_bro = ",".join(map(str, offsets['兄弟个数']))
            print(f"{seq:<6}{s_char:<10}{s_car:<10}{s_wea:<10}{s_bro:<10}")
            print("-" * 60)
            print("\n本命条文详细计算：")
            def print_calc(title, offset_list):
                for off in offset_list:
                    print(f"  {title}: {base} + {seq} + {off} = {base+seq+off}")
            print_calc("(1) 性格", offsets['性格'])
            print_calc("(2) 才能、前程", offsets['才能前程'])
            print_calc("(3) 财运", offsets['财运'])
            print_calc("(4) 兄弟个数", offsets['兄弟个数'])
        else:
            print(f"  [提示] 未在 14-10 表中找到匹配的条文数据 (卦名: {res['hex_name']}, 刻别: {res['moment_cn']}, 先天数: {res['cong_num']})")

        print("\n【流年条文 (1-100岁)】")
        print("=" * 220)
        # 打印表头（包含断语列）
        header_parts = [
            f"{'岁数':<6}", f"{'干支':<6}", f"{'四声':<6}", f"{'标记':<6}", f"{'字母':<6}",
            f"{'校正数':<8}", f"{'校正后校正数':<12}", f"{'计算公式':<10}",
            f"{'原条文':<8}", f"{'原断语':<30}", f"{'原断语年龄':<10}",
            f"{'校正后条文':<10}", f"{'校正后断语':<30}", f"{'校正后断语年龄':<10}"
        ]
        print("".join(header_parts))
        print("=" * 220)

        # 打印1-100岁的流年数据
        for i in [item for item in res['liunian'] if 1 <= item['age'] <= 100]:
            # 截断过长的断语，保持表格整洁
            original_duanyu = i['original_duanyu'][:28] + ".." if len(i['original_duanyu']) > 30 else i['original_duanyu']
            corrected_duanyu = i['corrected_duanyu'][:28] + ".." if len(i['corrected_duanyu']) > 30 else i['corrected_duanyu']

            row_parts = [
                f"{i['age']:<6}", f"{i['year']:<6}", f"{i['sound']:<6}", f"{i['marker']:<6}", f"{i['letter']:<6}",
                f"{i['original_correction']:<8}", f"{i['corrected_correction']:<12}", f"{i['formula']:<10}",
                f"{i['original_fortune']:<8}", f"{original_duanyu:<30}", f"{i['original_duanyu_age']:<10}",
                f"{i['corrected_fortune']:<10}", f"{corrected_duanyu:<30}", f"{i['corrected_duanyu_age']:<10}"
            ]
            print("".join(row_parts))
        print("=" * 220)

    def save_to_md(self, res, b_str, q_str):
        """保存排盘结果到Markdown文件"""
        if not os.path.exists("output"):
            os.makedirs("output")

        fname = f"output/铁板排盘_{b_str.split()[0]}_{q_str.split()[0]}.md"
        with open(fname, "w", encoding="utf-8") as f:
            # 写入基础信息
            f.write("# 铁板神数排盘结果\n\n")
            f.write(f"**排盘时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## 基础信息\n")
            f.write(f"```\n{res['header_info']}\n```\n\n")

            # 写入基础排盘数据
            f.write("## 基础排盘\n")
            f.write(f"- 先天命数：{res['cong_calc']}\n")
            f.write(f"- 五音命数：{res['tone_num']}\n")
            f.write(f"- 日命数 & 时运数：{res['day_life_calc']}\n")
            f.write(f"- 考刻结果：{res['moment_calc']}\n")
            f.write(f"- 本命数：{res['main_calc']}\n")
            f.write(f"- 十二辟卦：{res['hex_name']}\n\n")

            # 写入本命条文
            f.write("## 本命条文\n")
            if res['tbl_data']:
                tbl = res['tbl_data']
                base, seq, offsets = tbl['base'], tbl['seq'], tbl['offsets']
                f.write(f"**{res['moment_cn']}生人 - 先天命数 {res['cong_num']} - {res['hex_name']}(+{base})**\n\n")
                f.write("| 项目 | 数值 | 计算公式 |\n")
                f.write("|------|------|----------|\n")
                f.write(f"| 序数 | {seq} | - |\n")
                for item, values in offsets.items():
                    for val in values:
                        total = base + seq + val
                        f.write(f"| {item} | {total} | {base} + {seq} + {val} = {total} |\n")
            else:
                f.write("未找到匹配的本命条文数据\n\n")

            # 写入流年条文表格（包含断语）
            f.write("## 流年条文 (1-100岁)\n")
            f.write("| 岁数 | 干支 | 四声 | 标记 | 字母 | 校正数 | 校正后校正数 | 计算公式 | 原条文 | 原断语 | 原断语年龄 | 校正后条文 | 校正后断语 | 校正后断语年龄 |\n")
            f.write("|------|------|------|------|------|--------|--------------|----------|--------|--------|------------|------------|------------|----------------|\n")

            for i in [item for item in res['liunian'] if 1 <= item['age'] <= 100]:
                # 处理Markdown中的特殊字符
                original_duanyu = i['original_duanyu'].replace('|', '｜').replace('\n', ' ')
                corrected_duanyu = i['corrected_duanyu'].replace('|', '｜').replace('\n', ' ')

                f.write(f"| {i['age']} | {i['year']} | {i['sound']} | {i['marker']} | {i['letter']} | "
                        f"{i['original_correction']} | {i['corrected_correction']} | {i['formula']} | "
                        f"{i['original_fortune']} | {original_duanyu} | {i['original_duanyu_age']} | "
                        f"{i['corrected_fortune']} | {corrected_duanyu} | {i['corrected_duanyu_age']} |\n")

        print(f"\n[完成] 排盘报告已保存至: {os.path.abspath(fname)}")
