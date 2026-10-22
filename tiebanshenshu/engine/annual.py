"""108岁流年查表与未核实校正候选的生成。"""
import traceback


class AnnualCalculator:
    def __init__(self, db, fortune_lookup):
        self.db = db
        self.get_fortune_duanyu = fortune_lookup

    @staticmethod
    def get_liunian_groups(year_gan, year_zhi):
        b_group = "未知"
        if year_zhi in "寅午戌": b_group = "寅午戌"
        elif year_zhi in "申子辰": b_group = "申子辰"
        elif year_zhi in "巳酉丑": b_group = "巳酉丑"
        elif year_zhi in "亥卯未": b_group = "亥卯未"
        s_group = "未知"
        if year_gan in "甲乙丙丁": s_group = "甲乙丙丁"
        elif year_gan in "戊己": s_group = "戊己"
        elif year_gan in "庚辛": s_group = "庚辛"
        elif year_gan in "壬癸": s_group = "壬癸"
        return b_group, s_group

    @staticmethod
    def calculate_correction(original_correction, age):
        """
        根据年龄计算校正后的条文校正数
        规则：
        1. 1-10岁/81-108岁：校正数+2（>6则-6）
        2. 其他年龄：校正数+3（>20则-20）
        """
        if original_correction == 0:
            return 0

        # 情况一：1-10岁 或 81-108岁
        if (1 <= age <= 10) or (81 <= age <= 108):
            new_correction = original_correction + 2
            if new_correction > 6:
                new_correction -= 6
        # 情况二：其他年龄
        else:
            new_correction = original_correction + 3
            if new_correction > 20:
                new_correction -= 20

        return new_correction

    def calculate(self, cong_num, pn_num, moment_cn, y_gan, y_zhi):
        # Step 8: 计算流年条文（核心修改）
        liunian = []
        try:
            raw_seq = []
            final_seq = ["?"] * 12
            bg, sg = self.get_liunian_groups(y_gan, y_zhi)
            for k in [(cong_num, y_gan), (cong_num, sg)]:
                if k in self.db.LIUNIAN_SEQ:
                    raw_seq = self.db.LIUNIAN_SEQ[k]; break
            if raw_seq and len(raw_seq) >= 12:
                final_seq = raw_seq[:12]

            tg_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
            dz_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
            st_tg = tg_list.index(y_gan)
            st_dz = dz_list.index(y_zhi)

            # 生成1-108岁的流年数据（覆盖81-108岁的校正需求）
            for age in range(1, 109):
                cur_tg = tg_list[(st_tg + age - 1) % 10]
                cur_dz = dz_list[(st_dz + age - 1) % 12]
                sound = final_seq[(age - 1) % 12] if final_seq[0] != "?" else "?"
                marker = self.db.MARKER_TABLE.get(cur_dz, {}).get(pn_num, "?")

                age_parity = "奇数" if age % 2 != 0 else "偶数"
                letter = self.db.LETTER_TABLE.get((moment_cn, age_parity, sound, marker), "?")

                # 初始化变量
                base = 0
                add = 0
                original_correction = 0  # 原始条文校正数
                corrected_correction = 0  # 校正后的条文校正数
                original_fortune = ""     # 原始条文数
                corrected_fortune = ""    # 校正后的条文数
                formula = ""
                corrected_letter = ""     # 校正后的字母

                # 查找原始数据
                if letter != "?" and (letter, age) in self.db.DATA_BY_LETTER:
                    base, add, original_correction = self.db.DATA_BY_LETTER[(letter, age)]
                    formula = f"{base}+{add}"
                    original_fortune = str(base + add)

                    # 计算校正后的条文校正数
                    corrected_correction = self.calculate_correction(original_correction, age)

                    # 根据新的校正数查找校正后的条文
                    if corrected_correction > 0 and (corrected_correction, age) in self.db.DATA_BY_CORRECTION:
                        corr_base, corr_add = self.db.DATA_BY_CORRECTION[(corrected_correction, age)]
                        corrected_fortune = str(corr_base + corr_add)
                        # 查找校正后的字母（可选）
                        corrected_letter = self.db.CORRECTION_TO_LETTER.get((corrected_correction, age), "?")

                # ========== 新增：获取断语信息 ==========
                # 原始条文断语
                original_duanyu, original_duanyu_age = self.get_fortune_duanyu(original_fortune)
                # 校正后条文断语
                corrected_duanyu, corrected_duanyu_age = self.get_fortune_duanyu(corrected_fortune)

                # 构建流年数据
                liunian.append({
                    "age": age, 
                    "year": f"{cur_tg}{cur_dz}", 
                    "sound": sound,
                    "marker": marker, 
                    "letter": letter,
                    "corrected_letter": corrected_letter,
                    "original_correction": str(original_correction),
                    "corrected_correction": str(corrected_correction),
                    "formula": formula, 
                    "original_fortune": original_fortune,
                    "corrected_fortune": corrected_fortune,
                    "correction_status": "unverified_candidate",
                    "correction_applied": False,
                    # 新增断语字段
                    "original_duanyu": original_duanyu,          # 原始条文断语
                    "original_duanyu_age": original_duanyu_age,  # 原始条文对应年龄
                    "corrected_duanyu": corrected_duanyu,        # 校正后条文断语
                    "corrected_duanyu_age": corrected_duanyu_age # 校正后条文对应年龄
                })
        except Exception as e:
            print(f"计算流年数据时出错: {e}")
            traceback.print_exc()
            pass

        return liunian
