"""视频使用的互卦和四位组合；无默认卦、无旧引擎回退。"""
from .video_tables import LINES, BA_GUA_XIAN_TIAN, BA_GUA_HOU_TIAN

def get_hu_gua(upper, lower):
    lines = LINES[lower] + LINES[upper]
    inverse = {v:k for k,v in LINES.items()}
    hu_upper, hu_lower = inverse[lines[2:5]], inverse[lines[1:4]]
    return {'hu_shang_gua':hu_upper, 'hu_xia_gua':hu_lower,
            'hu_gua_name':hu_upper + '上' + hu_lower + '下'}

def gua_to_number(upper, lower, hu_upper, hu_lower, use_xian_tian=True):
    table = BA_GUA_XIAN_TIAN if use_xian_tian else BA_GUA_HOU_TIAN
    values = [table[g] for g in (upper,lower,hu_upper,hu_lower)]
    return {'number':sum(v * 10**(3-i) for i,v in enumerate(values))}
