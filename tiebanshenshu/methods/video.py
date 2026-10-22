"""视频公开步骤的可复算实现，不补造未公开的流度表或合化条件。"""
from .video_tables import (STEM_GUA, BRANCH_GUA, STEM_CODE, TRIGRAM_SUM,
    LINES, ANNUAL_STEM, ANNUAL_BRANCH, TIAN_GAN_TAI_XUAN, DI_ZHI_TAI_XUAN,
    BA_GUA_HOU_TIAN, BA_GUA_BY_XIAN_TIAN_NUM, BA_GUA_BY_HOU_TIAN_NUM,
    PARENT_BASES, PARENT_TABLE_SOURCE, reference_tables, VIDEO_TEXT_EVIDENCE)
from .video_hexagrams import get_hu_gua, gua_to_number

SOURCE = 'https://www.youtube.com/watch?v=o3mkGBcPkrI'


class VideoMethodCalculator:
    """每一条结果携带源时间；无已知事实时只给候选，不确定真刻。"""
    def __init__(self, verses=None):
        self.verses = verses or {}

    def article(self, number):
        entry = self.verses.get(number)
        evidence = VIDEO_TEXT_EVIDENCE.get(number)
        text_verified = bool(entry and evidence and entry[0].strip('。 ；;') == evidence['sentence'].strip('。 ；;'))
        return {'number': number, 'sentence': entry[0] if entry else '',
                'age': entry[1] if entry else '', 'found': entry is not None,
                'in_corpus': 1001 <= number <= 13000, 'fact_verified': False,
                'corpus_role':'comparison_only', 'video_edition_verified':False,
                'video_text_verified':text_verified,
                'video_text_evidence':evidence if text_verified else None}

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
        if not isinstance(stems, str) or len(stems) not in (4,5) or any(s not in STEM_CODE for s in stems):
            raise ValueError('编码须为四或五个已支持字符')
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
                'initial_ke_candidate':(initial-1)%8+1, 'shichen_shift':(initial-1)//8,
                'next_shichen_candidate':initial>8, 'status':'requires_fact_verification',
                'true_ke':None, 'upper':upper, 'lower':lower, 'mutual':hu,
                'thousands_rule':'(上卦先天数+6)%10', 'base_number':base,
                'secret_candidates':candidates, 'source_seconds':[172,348,425,632],
                'boundary_note':'超出条号13000的候选保留原算术并标记越界；视频边界口述尚不清晰，不擅自循环。'}

    def parent_candidates(self, known_parents=None):
        """生肖只能定位基条，不能自动证明干支年或真刻。"""
        known_parents = {} if known_parents is None else known_parents
        if not isinstance(known_parents, dict):
            raise ValueError('父母生肖须为对象')
        rows = []
        for relation, animal in known_parents.items():
            if relation not in PARENT_BASES or not isinstance(animal,str) or animal not in PARENT_BASES[relation]:
                raise ValueError('只支持父亲、母亲及十二生肖')
        for relation in ('父亲','母亲'):
            if relation not in known_parents:
                continue
            animal=known_parents[relation]
            base = PARENT_BASES[relation][animal]
            rows.append({'relation':relation,'animal':animal,'base_number':base,
                         'base_article':self.article(base),
                         'year_candidates':[self.article(base+10*i) for i in range(5)],
                         'status':'requires_full_year_verse_verification',
                         'source_seconds':[690,900], 'table_source':PARENT_TABLE_SOURCE,
                         'note':'依视频展示基条与逐加10；对照库存在缺失和不同条文，不能按生肖自动选定干支年份。'})
        return rows

    def life_sequence(self, base):
        """26:20–27:10逐加96，超过13000减12000，回到起点即停止。"""
        if type(base) is not int or not 1001 <= base <= 13000:
            raise ValueError('论命基数须在1001至13000之间')
        rows=[]
        seen=set()
        number=base
        while number not in seen:
            seen.add(number)
            rows.append(self.article(number))
            number += 96
            if number > 13000:
                number -= 12000
        return {'base':base,'step':96,'wrap_above':13000,'wrap_subtract':12000,
                'articles':rows,'stop_reason':'cycle_complete',
                'note':'只按数字轮转，不自动识别寿终，不把寿命类条文当成真实寿命。',
                'source_seconds':[1580,1625]}

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
                **calculation, 'jiaze_source_seconds':calculation['source_seconds'],
                'source_seconds':[1494,1575], 'article':self.article(calculation['number'])}

    def sequence_article(self, raw_number):
        """96条号序列按同一12000条区间轮转，保留原算术数供核对。"""
        number=1001+(raw_number-1001)%12000
        return {**self.article(number),'arithmetic_number':raw_number,
                'range_adjustment':number-raw_number}

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
                'articles': [self.sequence_article(base + direction*96*i) for i in range(1,5)],
                'source_seconds': [1928,2012]}

    def before_after(self, bazi, benming_gua_number=None):
        """承接31:50太玄配数说明及32–33分前/后卦文字卡。"""
        def make(position_upper, position_lower, xian):
            traces=[]
            table=BA_GUA_BY_XIAN_TIAN_NUM if xian else BA_GUA_BY_HOU_TIAN_NUM
            guas=[]
            for position in (position_upper,position_lower):
                pillar=bazi[position]
                values=[TIAN_GAN_TAI_XUAN[pillar[0]],DI_ZHI_TAI_XUAN[pillar[1]]]
                total=sum(values); reduced=total % 8 or 8
                traces.append({'position':position,'pillar':pillar,'values':values,
                               'sum':total,'remainder_mod8':total % 8,'trigram_number':reduced})
                guas.append(table.get(reduced))
            source=[1928,1980] if xian else [1980,2012]
            if any(g is None for g in guas):
                return {'status':'requires_middle_five_rule','articles':[],
                        'pillar_steps':traces,'source_seconds':source,
                        'note':'太玄除8余数为5；后天5居中，视频未给本分支的寄卦规则，不能自动换卦。'}
            upper,lower=guas
            hu=get_hu_gua(upper,lower)
            combination=gua_to_number(upper,lower,hu['hu_shang_gua'],hu['hu_xia_gua'],xian)['number']
            base=combination+benming_gua_number if benming_gua_number is not None else None
            direction=1 if xian else -1
            return {'upper':upper,'lower':lower,'mutual':hu,'pillar_steps':traces,
                    'combination':combination,'benming_gua_number':benming_gua_number,
                    'base':base,'direction':direction,'step':96,
                    'status':'calculated' if base is not None else 'requires_benming_gua_number',
                    'articles':[self.sequence_article(base+direction*96*i) for i in range(1,5)] if base is not None else [],
                    'source_seconds':source,
                    'rule_basis':'承接同段太玄除8方法，前卦查先天数表，后卦查后天数表；后卦为规则推导结果，非白板已列答案。'}
        return {'before':make('month','year',True),'after':make('time','day',False)}

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

    def calculate(self,bazi,confirmed_number=None,benming_gua_number=None,fortune_pillar=None,known_parents=None,basis_number=None):
        self.validate_pillars(bazi)
        if benming_gua_number is not None and (type(benming_gua_number) is not int or not 1<=benming_gua_number<=13000):
            raise ValueError('本命卦数须为1至13000的整数')
        if basis_number is not None and confirmed_number is not None and basis_number != confirmed_number:
            raise ValueError('演算基数与已核验基数不能同时填写为不同数值')
        supplied = confirmed_number if confirmed_number is not None else basis_number
        number_result = self.number_method(bazi,supplied) if supplied is not None else {'status':'requires_basis_number'}
        if supplied is not None:
            number_result['input_number']=supplied
            number_result['input_fact_verified']=confirmed_number is not None
            number_result['input_role']='fact_confirmed' if confirmed_number is not None else 'arithmetic_only'
            if confirmed_number is None and number_result['status']=='calculated_from_caller_confirmed_number':
                number_result['status']='calculated_from_candidate_number'
        derived = number_result.get('number')
        if benming_gua_number is None and type(derived) is int and 1001 <= derived <= 13000:
            benming_gua_number=derived
            benming_basis='接续视频25:50–26:15化卦加则所得推命基数；32:30文字卡加本命卦数，按上下文衔接'
        else:
            benming_basis='caller_supplied' if benming_gua_number is not None else 'requires_basis_number'
        before_after=self.before_after(bazi,benming_gua_number)
        before_after['benming_basis']=benming_basis
        life = self.life_sequence(number_result['number']) if type(number_result.get('number')) is int and 1001 <= number_result['number'] <= 13000 else None
        return {'method':'zefang_video_o3mkGBcPkrI','source':SOURCE,
                'scope':'按视频连续演算；条文对照不阻断数值推导，未核验事实不自动定真刻',
                'reference_tables':reference_tables(),
                'source_conflicts':[{'topic':'流年天干排列', 'overlay_order':'年月日时',
                    'worked_example_order':'月日時年','implementation':'采用口述及白板6464算例顺序',
                    'source_seconds':[1745,1867]}],
                'bazi':bazi,'preliminary':self.preliminary(bazi),
                'parent_candidates':self.parent_candidates(known_parents),
                'pillar_articles':self.pillar_articles(bazi),
                'number_method':number_result, 'life_sequence':life,
                'before_after':before_after,
                'annual':self.annual_example(bazi,fortune_pillar) if fortune_pillar is not None else None,
                'unresolved':['乾坤甲流度干支年份条文底本（固定生肖表已接入）','合化完整条件','1327候选的越界规则（不套用96轮转规则）']}
