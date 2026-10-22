"""六亲考刻和扩展规则的组合服务。"""
from tiebanshenshu.kaoke.annual import (
    calculate_baisui_liunian_peishu,
    calculate_baisui_liunian_zai_e,
)
from tiebanshenshu.kaoke.candidates import (
    kao_ke,
    zhidu_tiaowen,
)
from tiebanshenshu.kaoke.derived import (
    calculate_he_luo_peishu,
    calculate_liuqin_shengxiao_mifa,
    calculate_yinyun_baiqie,
)
from tiebanshenshu.kaoke.hexagrams import (
    calculate_houtian_yuncheng,
    calculate_kaoke_qushu,
)
from tiebanshenshu.kaoke.numbers import (
    calculate_base_number,
    calculate_huangji_total,
    calculate_liuqin_ming_shu,
    calculate_liuqin_shengxiao_range,
    calculate_renyuan_shu,
    get_tiaowen_by_topic,
)
from tiebanshenshu.kaoke.orchestrator import (
    calculate_keke,
)
from tiebanshenshu.kaoke.relatives import (
    calculate_xinyi_brother_count,
)


class ExtensionCalculator:
    """组合独立扩展规则，不修改十四表的本命和流年结果。"""
    def __init__(self, db):
        self.db = db

    def calculate(self, birth, query, gender, cong_num, y_gan, known_shengxiao):
        keke_result = calculate_keke(birth, query, self.db.FORTUNE_DUANYU_MAP, self.db)
        result = keke_result or {}
        if keke_result:
            if known_shengxiao:
                k_true, ba_ke_results, kao_ke_info = kao_ke(keke_result['liuqinjishu'], known_shengxiao, self.db)
                result['k_true'] = k_true
                result['ba_ke_results'] = ba_ke_results
                result['kao_ke_info'] = kao_ke_info
                if k_true is not None:
                    result['tiaowen'] = zhidu_tiaowen(keke_result['liuqinjishu'], k_true, self.db)

        bazi = birth['bazi']

        result['he_luo_peishu'] = calculate_he_luo_peishu(bazi)
        result['yinyun_baiqie'] = calculate_yinyun_baiqie(bazi)
        result['liuqin_shengxiao_mifa'] = calculate_liuqin_shengxiao_mifa(bazi)
        result['baisui_liunian_peishu'] = calculate_baisui_liunian_peishu(bazi)
        result['baisui_liunian_zai_e'] = calculate_baisui_liunian_zai_e(bazi)

        result['base_number'] = calculate_base_number(bazi)

        core = result['base_number']['base']
        result['core_number'] = core

        secret_table = self.db.SECRET_NUMBER_TABLE
        result['secret_number_table'] = secret_table

        tiaowen_by_topic = {}
        for topic in secret_table:
            tiaowen_by_topic[topic] = get_tiaowen_by_topic(core, topic, self.db.FORTUNE_DUANYU_MAP, secret_table)
        result['tiaowen_by_topic'] = tiaowen_by_topic

        result['huangji_total'] = calculate_huangji_total(bazi)

        result['liuqin_shengxiao_range'] = calculate_liuqin_shengxiao_range(bazi)

        result['renyuan_shu'] = calculate_renyuan_shu(cong_num, y_gan)

        result['liuqin_ming_shu'] = calculate_liuqin_ming_shu(cong_num)

        result['kaoke_qushu'] = calculate_kaoke_qushu(bazi, gender, self.db)

        result['houtian_yuncheng'] = calculate_houtian_yuncheng(bazi, self.db)

        result['xinyi_brother_count'] = calculate_xinyi_brother_count(bazi, self.db)

        return result
