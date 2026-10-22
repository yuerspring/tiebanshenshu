"""视频公开步骤的可复算实现，不补造未公开的流度表或合化条件。"""
from .video_tables import (STEM_GUA, BRANCH_GUA, STEM_CODE, TRIGRAM_SUM,
                           LINES, ANNUAL_STEM, ANNUAL_BRANCH)
from tiebanshenshu.tables.numbers import TIAN_GAN_TAI_XUAN, DI_ZHI_TAI_XUAN
from tiebanshenshu.tables.kinship import BA_GUA_HOU_TIAN, BA_GUA_BY_XIAN_TIAN_NUM, BA_GUA_BY_HOU_TIAN_NUM
from tiebanshenshu.kaoke.hexagrams import get_hu_gua, gua_to_number

SOURCE = 'https://www.youtube.com/watch?v=o3mkGBcPkrI'


class VideoMethodCalculator:
    """每一条结果携带源时间；无已知事实时只给候选，不确定真刻。"""
    def __init__(self, verses=None):
        self.verses = verses or {}

    def article(self, number):
        entry = self.verses.get(number)
        return {'number': number, 'sentence': entry[0] if entry else '',
                'age': entry[1] if entry else '', 'found': entry is not None,
                'in_corpus': 1001 <= number <= 13000, 'fact_verified': False}

    @staticmethod
    def validate_pillars(bazi):
        if not isinstance(bazi, dict):
            raise ValueError('需要四柱')
        for key in ('year','month','day','time'):
            value = bazi.get(key)
            if not isinstance(value, str) or len(value) != 2 or value[0] not in TIAN_GAN_TAI_XUAN or value[1] not in DI_ZHI_TAI_XUAN:
                raise ValueError('四柱须为有效天干地支字符')

    @staticmethod
    def encode_stems(stems):
        if not isinstance(stems, str) or len(stems) != 4 or any(s not in STEM_CODE for s in stems):
            raise ValueError('编码须为四个已支持字符')
        return int(''.join(str(STEM_CODE[s]) for s in stems))

    @staticmethod
    def jiaze(upper, lower):
        """19:40–22:30：阴阳爻分别自上往下纳支，再取千位并减下卦。"""
        if upper not in LINES or lower not in LINES:
            raise ValueError('无效八卦')
        counts = {0: 0, 1: 0}
        values = []
        for yang in reversed(LINES[lower] + LINES[upper]):
            counts[yang] += 1
            values.append(30 * counts[yang])
        number = BA_GUA_HOU_TIAN[upper] * 1000 + sum(values) - BA_GUA_HOU_TIAN[lower]
        return {'upper':upper, 'lower':lower, 'line_values_top_down':values,
                'line_sum':sum(values), 'number':number, 'source_seconds':[1180,1342]}

    def pillar_articles(self, bazi):
        rows = []
        for position in ('year','month','day','time'):
            stem, branch = bazi[position]
            upper, lower = STEM_GUA[stem], BRANCH_GUA[branch]
            first = self.jiaze(upper, lower)
            second = TRIGRAM_SUM[upper][0] * 100 + TRIGRAM_SUM[lower][1]
            rows.append({'position':position, 'pillar':bazi[position], 'jiaze':first,
                         'jiaze_article':self.article(first['number']),
                         'stem_branch_sum_number':second, 'sum_article':self.article(second),
                         'sum_source_seconds':[1370,1438]})
        return rows

    def preliminary(self, bazi):
        pairs = [[TIAN_GAN_TAI_XUAN[bazi[k][0]],DI_ZHI_TAI_XUAN[bazi[k][1]]]
                 for k in ('year','month','day','time')]
        total = sum(map(sum,pairs))
        divisor = '子丑寅卯辰巳午未申酉戌亥'.index(bazi['time'][1]) + 1
        remainder = total % divisor
        # 05:40 的明确口述为余0暂作一刻。不是事实核验结果。
        initial = remainder or 1
        upper_n, lower_n = sum(pairs[1]) % 8 or 8, sum(pairs[0]) % 8 or 8
        upper, lower = BA_GUA_BY_XIAN_TIAN_NUM[upper_n], BA_GUA_BY_XIAN_TIAN_NUM[lower_n]
        hu = get_hu_gua(upper,lower)
        plain = gua_to_number(upper,lower,hu['hu_shang_gua'],hu['hu_xia_gua'])['number']
        # 07:30/09:10：固定加6，不能误写成加互上卦。
        thousands = (upper_n + 6) % 10
        base = thousands * 1000 + plain % 1000
        candidates = [{**self.article(base + 1327*m), 'multiplier':m}
                      for m in (0,1,2,4,6,8,10,12,14)]
        return {'sum':total, 'pairs':pairs, 'hour_divisor':divisor, 'remainder':remainder,
                'initial_ke_candidate':initial if initial <= 8 else 1 if initial == 9 else None,
                'next_shichen_candidate':initial>8, 'status':'requires_fact_verification',
                'true_ke':None, 'upper':upper, 'lower':lower, 'mutual':hu,
                'thousands_rule':'(上卦先天数+6)%10', 'base_number':base,
                'secret_candidates':candidates, 'source_seconds':[172,348,425,632],
                'boundary_note':'超出条号13000的候选保留原算术并标记越界；视频边界口述尚不清晰，不擅自循环。'}

    def number_method(self, bazi, confirmed_number):
        """24:50–28:40；只接受调用者已经核验的基数，不从生肖猜选。"""
        if type(confirmed_number) is not int or not 1001 <= confirmed_number <= 9999:
            raise ValueError('已核验基数须为1001至9999的四位整数')
        digits = list(map(int,str(confirmed_number)))
        sums = [sum(digits[:2]),sum(digits[2:])]
        if any(n in (5,10) for n in sums):
            code = self.encode_stems(''.join(bazi[k][0] for k in ('month','day','time','year')))
            return {'status':'four_stem_fallback', 'pair_sums':sums,
                    'number':code, 'article':self.article(code), 'source_seconds':[1537,1719]}
        values = [n-8 if n>8 else n for n in sums]
        if any(v not in BA_GUA_BY_HOU_TIAN_NUM or v==5 for v in values):
            return {'status':'unresolved_pair_boundary', 'pair_sums':sums,
                    'number':None, 'source_seconds':[1494,1548]}
        upper,lower = [BA_GUA_BY_HOU_TIAN_NUM[v] for v in values]
        calculation = self.jiaze(upper,lower)
        return {'status':'calculated_from_caller_confirmed_number', 'pair_sums':sums,
                **calculation, 'article':self.article(calculation['number'])}

    def series_for_gua(self, upper, lower, benming_gua_number, use_xian_tian=True):
        """已给定卦与本命卦数时，执行视频明确公开的前加、后减96。"""
        if upper not in LINES or lower not in LINES:
            raise ValueError('无效八卦')
        if type(benming_gua_number) is not int or not 1 <= benming_gua_number <= 13000:
            raise ValueError('本命卦数须为1至13000的整数')
        hu = get_hu_gua(upper, lower)
        combination = gua_to_number(upper, lower, hu['hu_shang_gua'], hu['hu_xia_gua'], use_xian_tian)['number']
        base = combination + benming_gua_number
        direction = 1 if use_xian_tian else -1
        return {'combination': combination, 'base': base,
                'articles': [self.article(base + direction*96*i) for i in range(1,5)],
                'source_seconds': [1928,2012]}

    def before_after(self, bazi, benming_gua_number=None):
        """32:00–33:40：前卦已演示；后卦柱配数规则不补猜。"""
        def value(key):
            p = bazi[key]
            return (TIAN_GAN_TAI_XUAN[p[0]] + DI_ZHI_TAI_XUAN[p[1]]) % 8 or 8
        upper = BA_GUA_BY_XIAN_TIAN_NUM[value('month')]
        lower = BA_GUA_BY_XIAN_TIAN_NUM[value('year')]
        hu = get_hu_gua(upper, lower)
        combination = gua_to_number(upper, lower, hu['hu_shang_gua'], hu['hu_xia_gua'])['number']
        base = combination + benming_gua_number if benming_gua_number is not None else None
        return {
            'before': {'upper': upper, 'lower': lower, 'mutual': hu,
                       'combination': combination, 'benming_gua_number': benming_gua_number,
                       'base': base,
                       'status': 'calculated' if base is not None else 'requires_benming_gua_number',
                       'articles': [self.article(base + 96*i) for i in range(1,5)] if base is not None else [],
                       'source_seconds': [1928,1980]},
            'after': {'status': 'requires_houtian_conversion_rule', 'articles': [],
                      'note': '视频规定时上日下、逐次减96，但未完整演示后天柱配数边界；不借用其他书的减10默认法。',
                      'source_seconds': [1980,2012]},
        }

    def annual_example(self, bazi, fortune_pillar):
        """30:00–31:15 的未合化分支；不自动推大运起岁或合化。"""
        if not isinstance(fortune_pillar,str) or len(fortune_pillar)!=2 or fortune_pillar[0] not in ANNUAL_STEM or fortune_pillar[1] not in ANNUAL_BRANCH:
            raise ValueError('运柱须为有效天干地支字符')
        values=[ANNUAL_STEM[bazi[k][0]] for k in ('month','day','time','year')]
        base=int(''.join(map(str,values))); stem=ANNUAL_STEM[fortune_pillar[0]]
        branches=ANNUAL_BRANCH[fortune_pillar[1]]; number=base+stem+sum(branches)
        return {'base':base,'stem_add':stem,'branch_add':list(branches),'number':number,
                'article':self.article(number),'status':'untransformed_branch_only',
                'note':'未自动判定合化；视频未完整给出全部条件，也未实现大运起岁。',
                'source_seconds':[1741,1904]}

    def calculate(self,bazi,confirmed_number=None,benming_gua_number=None,fortune_pillar=None):
        self.validate_pillars(bazi)
        if benming_gua_number is not None and (type(benming_gua_number) is not int or not 1<=benming_gua_number<=13000):
            raise ValueError('本命卦数须为1至13000的整数')
        return {'method':'zefang_video_o3mkGBcPkrI','source':SOURCE,
                'scope':'公开步骤复算；不宣称完整自动考刻或预测准确率',
                'bazi':bazi,'preliminary':self.preliminary(bazi),
                'pillar_articles':self.pillar_articles(bazi),
                'number_method':self.number_method(bazi,confirmed_number) if confirmed_number is not None else {'status':'requires_confirmed_number'},
                'before_after':self.before_after(bazi,benming_gua_number),
                'annual':self.annual_example(bazi,fortune_pillar) if fortune_pillar is not None else None,
                'unresolved':['乾坤甲流度完整表与干支年份验条','本命卦数的统一来源','合化完整条件','越界循环口述']}
