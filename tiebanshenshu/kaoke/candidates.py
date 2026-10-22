"""钟表八刻与六亲条件候选核对。"""
from tiebanshenshu.tables.kinship import (
    DI_ZHI_TO_SHENG_XIAO,
    LIU_QIN_TYPE_CODES,
    SHENG_XIAO_TO_DIZHI,
)
from tiebanshenshu.tables.numbers import (
    DI_ZHI_ORDER,
)

def get_kefen(hour, minute):
    """确定时辰八刻"""
    adjusted_hour = hour
    if adjusted_hour == 0:
        adjusted_hour = 24
    
    shichen_start = ((adjusted_hour - 1) // 2) * 2 + 1
    if shichen_start == 25:
        shichen_start = 1
    
    minute_in_shichen = ((adjusted_hour - shichen_start) * 60) + minute
    
    k = (minute_in_shichen // 15) + 1
    if k > 8: k = 8
    if k < 1: k = 1
    
    return k, minute_in_shichen

def kao_ke(liuqinjishu, known_liuqinshengxiao, db=None):
    """Expose legacy numeric candidates without inventing a successful match.

    The inherited decimal-digit rule is not verified against a fixed book.
    In particular, it cannot represent zodiac orders 11 and 12. Those inputs
    stay unassessed rather than being forced into a false first-quarter match.
    """
    relations = [name for name in ('父亲', '母亲', '兄弟', '配偶', '子女')
                 if name in known_liuqinshengxiao and name in liuqinjishu
                 and known_liuqinshengxiao[name] in SHENG_XIAO_TO_DIZHI]
    if not relations:
        return None, None, None

    unsupported = [name for name in relations
                   if DI_ZHI_ORDER[SHENG_XIAO_TO_DIZHI[known_liuqinshengxiao[name]]] > 10]
    candidates = []
    for k in range(1, 9):
        evidence = []
        for name in relations:
            target = known_liuqinshengxiao[name]
            target_zhi = SHENG_XIAO_TO_DIZHI[target]
            base = liuqinjishu[name]
            value = base + k
            digit = value % 10 or 10
            predicted_zhi = next((zhi for zhi, order in DI_ZHI_ORDER.items()
                                  if order == digit), '')
            supported = name not in unsupported
            code = LIU_QIN_TYPE_CODES.get(name, 0) + value * 10 + DI_ZHI_ORDER[target_zhi]
            text, age = ('', '')
            if db is not None and hasattr(db, 'FORTUNE_DUANYU_MAP'):
                text, age = db.FORTUNE_DUANYU_MAP.get(code, ('', ''))
            evidence.append({
                'relation': name, 'target_shengxiao': target, 'base': base,
                'C_i': value, 'gewei': digit,
                'calculated_zhi': predicted_zhi,
                'calculated_shengxiao': DI_ZHI_TO_SHENG_XIAO.get(predicted_zhi, ''),
                'supported': supported,
                'match': predicted_zhi == target_zhi if supported else None,
                'code': code, 'duanyu': text, 'age': age,
                'text_verified': False,
            })
        matches = sum(item['match'] is True for item in evidence)
        conflicts = sum(item['match'] is False for item in evidence)
        candidates.append({
            'k': k, 'conditions': evidence, 'matched_conditions': matches,
            'conflicting_conditions': conflicts,
            'unassessed_conditions': len(unsupported),
            'match': matches == len(relations) and not unsupported,
        })
    surviving = [row['k'] for row in candidates if row['conflicting_conditions'] == 0]
    matching = [row['k'] for row in candidates if row['match']]
    selected = matching[0] if len(matching) == 1 else None
    status = ('no_match' if not surviving else
              'unsupported' if unsupported else
              'unique_candidate' if selected is not None else
              'ambiguous' if matching else 'no_match')
    return selected, candidates, {
        'method': 'legacy_decimal_digit', 'source_status': 'unverified',
        'status': status, 'used_relations': relations,
        'liuqin_type': relations[0] if len(relations) == 1 else None,
        'unsupported_relations': unsupported,
        'k_true': selected, 'candidate_ks': matching, 'supported_candidate_ks': surviving,
        'match_count': len(matching),
        'note': '旧版数值候选不等于古籍验条或事实验证；无匹配不指定刻，狗/猪规则尚不支持。',
    }

def zhidu_tiaowen(liuqinjishu, k_true, db=None):
    """锁定刻分后的条文直读（关联实际条文内容）"""
    results = {}
    
    for liuqin_type, B in liuqinjishu.items():
        C = B + k_true
        type_code = LIU_QIN_TYPE_CODES.get(liuqin_type, 0)
        
        for shengxiao, zhi in SHENG_XIAO_TO_DIZHI.items():
            S = DI_ZHI_ORDER.get(zhi, 0)
            code = type_code + C * 10 + S
            
            tiaowen_text = None
            tiaowen_age = ""
            if db and hasattr(db, 'FORTUNE_DUANYU_MAP') and code in db.FORTUNE_DUANYU_MAP:
                tiaowen_text, tiaowen_age = db.FORTUNE_DUANYU_MAP[code]
            
            results[f"{liuqin_type}_{shengxiao}"] = {
                "liuqin": liuqin_type,
                "shengxiao": shengxiao,
                "base": B,
                "ke": k_true,
                "C": C,
                "code": code,
                "tiaowen": tiaowen_text,
                "age": tiaowen_age
            }
    
    return results

__all__ = [
    'get_kefen',
    'kao_ke',
    'zhidu_tiaowen',
]
