"""十四表主流程：本命计算与各服务的组合。"""
from tiebanshenshu.data.loader import TieBanDataLoader
from tiebanshenshu.engine.annual import AnnualCalculator
from tiebanshenshu.engine.extensions import ExtensionCalculator
from tiebanshenshu.presentation.reports import ReportWriter
from tiebanshenshu.tables.core import (
    NAYIN_WUXING,
)


class TieBanCalculator:
    def __init__(self):
        self.loader = TieBanDataLoader()
        self.db = self.loader
        self.tiangan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.dizhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    def get_gan_group(self, gan):
        if gan not in self.tiangan: return "甲己"
        return ["甲己", "乙庚", "丙辛", "丁壬", "戊癸"][self.tiangan.index(gan) % 5]

    def is_yang_year(self, year_gan):
        return year_gan in ["甲", "丙", "戊", "庚", "壬"]

    def get_fortune_duanyu(self, fortune_num):
        """
        根据条文数字获取对应的断语和年龄
        返回：(断语, 对应年龄)
        """
        if not fortune_num or fortune_num == "" or not self._is_numeric(fortune_num):
            return ("", "")

        try:
            num = int(float(fortune_num))
            return self.db.FORTUNE_DUANYU_MAP.get(num, ("未找到断语", "未知"))
        except:
            return ("", "")

    def _is_numeric(self, value):
        """判断值是否可以转换为数字"""
        if not value:
            return False
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def calculate(self, payload):
        birth, query, gender = payload['birth_info'], payload['query_info'], payload['gender']
        y_gan, y_zhi = birth['bazi']['year'][0], birth['bazi']['year'][1]
        t_zhi = birth['bazi']['time'][1]
        d_day, t_gan, t_time = birth['bazi']['day'], query['bazi']['time'][0], query['bazi']['time']

        details = {}
        details['header_info'] = f"性别:{gender}, 农历:{birth['lunar_str']}，闰月{'是' if birth['is_leap'] else '否'}，出生八字：{birth['bazi']['year']} {birth['bazi']['month']} {birth['bazi']['day']} {birth['bazi']['time']}\n求测日期：阳历：{query['date_str']}     八字：{query['bazi']['year']} {query['bazi']['month']} {query['bazi']['day']} {query['bazi']['time']}"

        # Step 1: 计算先天命数
        calc_month = str(m_idx := birth['lunar_month'] + (1 if birth['is_leap'] else 0))
        if int(m_idx) > 12: calc_month = "1"
        month_val = self.db.tables['14-1'][calc_month]
        time_val = self.db.tables['14-2'][t_zhi]
        cong_num = month_val + 3 - time_val
        cong_num = ((cong_num - 1) % 12) + 1
        details['cong_calc'] = f"先天命数 = {cong_num}"
        details['cong_num'] = cong_num

        # Step 2: 计算五音命数
        gan_group = self.get_gan_group(y_gan)
        tone = self.db.tables['14-3'][cong_num][gan_group]
        tone_num = self.db.tables['14-4'][tone]
        details['tone_num'] = tone_num

        # Step 3: 计算日命数和时运数
        day_n = NAYIN_WUXING[d_day]
        day_life = self.db.tables['14-5'][day_n][t_gan]
        time_n = NAYIN_WUXING[t_time]
        time_luck = self.db.tables['14-6'][time_n]
        details['day_life_calc'] = f"日命:{day_life}, 时运:{time_luck}"

        # Step 4: 确定刻别（初刻/正刻）
        sum_val = day_life + time_luck
        is_yang = self.is_yang_year(y_gan)
        grp = "阳男阴女" if (gender == "男" and is_yang) or (gender == "女" and not is_yang) else "阴男阳女"

        if (gender == "男" and is_yang) or (gender == "女" and not is_yang):
            if sum_val > 6:
                moment_cn = "初刻"
            else:
                moment_cn = "正刻"
        else:
            if sum_val > 6:
                moment_cn = "正刻"
            else:
                moment_cn = "初刻"

        moment = "Initial" if moment_cn == "初刻" else "Main"
        details['moment_calc'] = f"考刻: {moment_cn} (日命数:{day_life},时运数:{time_luck},和:{sum_val},性别:{gender},年干:{y_gan}{'阳' if is_yang else '阴'},{grp})"
        details['moment_cn'] = moment_cn

        # Step 5: 计算本命数
        sum_val = day_life + time_luck
        if sum_val <= 6:
            main_num = (tone_num * 5 + day_life + time_luck - 1) * 30 + birth['lunar_day']
            details['main_calc'] = f"本命数=(五音命数×5+日命数+时运数-1)×30+农历出生日=({tone_num}×5+{day_life}+{time_luck}-1)×30+{birth['lunar_day']}={main_num}"
        else:
            main_num = (tone_num * 5 + day_life + time_luck - 6) * 30 + birth['lunar_day']
            details['main_calc'] = f"本命数=(五音命数×5+日命数+时运数-6)×30+农历出生日=({tone_num}×5+{day_life}+{time_luck}-6)×30+{birth['lunar_day']}={main_num}"
        details['main_num'] = main_num

        # Step 6: 查找卦名
        hex_name = self.db.HEXAGRAM_DETAIL_MAP.get((moment_cn, main_num))
        details['hexagram_source'] = {
            'table': '14-9.csv', 'moment': moment_cn, 'main_num': main_num,
            'found': hex_name is not None, 'fallback_used': False,
        }
        details['data_warnings'] = []
        if hex_name is None:
            # Never silently borrow the initial-quarter entry for a missing
            # main-quarter key. The corpus must be corrected from a source.
            hex_name = f"未知(刻别:{moment_cn},本命数:{main_num}未匹配)"
            details['data_warnings'].append({
                'code': 'MISSING_HEXAGRAM_ENTRY', 'table': '14-9.csv',
                'message': f'14-9.csv 缺少{moment_cn}/{main_num}，未借用其他刻别生成本命条文。',
            })
        details['hex_name'] = hex_name

        # 查找详细数据
        tbl_data = self.db.DESTINY_DATA.get((hex_name, moment, cong_num))
        details['tbl_data'] = tbl_data

        # Step 7: 计算后天命数
        pn_sum = cong_num + main_num
        pn_num = pn_sum % 8
        if pn_num == 0: pn_num = 8
        details['pn_log'] = f"先天命数＋本命数＝{cong_num}＋{main_num}＝{pn_sum}÷8→余数＝{pn_num}"
        details['pn_num'] = pn_num

        details['liunian'] = AnnualCalculator(self.db, self.get_fortune_duanyu).calculate(
            cong_num, pn_num, moment_cn, y_gan, y_zhi,
        )

        details['keke'] = ExtensionCalculator(self.db).calculate(
            birth, query, gender, cong_num, y_gan, payload.get('known_shengxiao', {}),
        )

        return details

    def get_liunian_groups(self, year_gan, year_zhi):
        return AnnualCalculator.get_liunian_groups(year_gan, year_zhi)

    def calculate_correction(self, original_correction, age):
        return AnnualCalculator.calculate_correction(original_correction, age)

    def print_report(self, res):
        return ReportWriter().print_report(res)

    def save_to_md(self, res, b_str, q_str):
        return ReportWriter().save_to_md(res, b_str, q_str)
