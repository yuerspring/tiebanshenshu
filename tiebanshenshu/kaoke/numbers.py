"""基础配数、起宿与事项条号。"""
from tiebanshenshu.tables.numbers import (
    DI_YUAN_SHU,
    DI_ZHI_TAI_XUAN,
    DONG_GUA_CE_SHU,
    ER_SHI_BA_SU,
    LIAN_SHAN_GUA_SHU,
    LIU_QIN_MING_SHU_FORMULA,
    LIU_SHI_JIA_ZI_DI_LI_CHENG_DING_SHU,
    NIAN_CHU_SHU,
    QI_YUAN_QI_SU,
    SECRET_NUMBER_TABLE,
    SHENG_XIAO_FAN_WEI,
    SU_XIU_PEI_SHU,
    TIAN_GAN_TAI_XUAN,
    TIAN_YUAN_SHU,
)

def get_tai_xuan(gan, zhi):
    """获取天干和地支的太玄数"""
    return TIAN_GAN_TAI_XUAN.get(gan, 0), DI_ZHI_TAI_XUAN.get(zhi, 0)

def get_jiayun(year_gan_zhi):
    """确定年柱所属的甲旬"""
    for yuan_name, yuan_data in QI_YUAN_QI_SU.items():
        if year_gan_zhi in yuan_data["甲旬"]:
            return yuan_name, yuan_data["起宿"]
    return "甲子元", "虚日鼠"

def get_day_su(xinqi1_su, day_offset):
    """计算某日的值日星宿"""
    if xinqi1_su not in ER_SHI_BA_SU:
        return None, None
    
    start_idx = ER_SHI_BA_SU.index(xinqi1_su)
    offset = (day_offset - 1) % 28
    day_su = ER_SHI_BA_SU[(start_idx + offset) % 28]
    su_shu = SU_XIU_PEI_SHU.get(day_su, 0)
    
    return day_su, su_shu

def get_hour_su(day_su, hour_zhi):
    """计算某时辰的星宿"""
    if day_su not in ER_SHI_BA_SU:
        return None, None
    
    dizhi_order_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    if hour_zhi not in dizhi_order_list:
        return None, None
    
    day_su_idx = ER_SHI_BA_SU.index(day_su)
    hour_offset = dizhi_order_list.index(hour_zhi)
    hour_su = ER_SHI_BA_SU[(day_su_idx + hour_offset) % 28]
    su_shu = SU_XIU_PEI_SHU.get(hour_su, 0)
    
    return hour_su, su_shu

def calculate_liuqinjishu(bazi, D, H):
    """计算六亲基数"""
    year_gan, year_zhi = bazi['year'][0], bazi['year'][1]
    month_gan, month_zhi = bazi['month'][0], bazi['month'][1]
    day_gan, day_zhi = bazi['day'][0], bazi['day'][1]
    time_gan, time_zhi = bazi['time'][0], bazi['time'][1]
    
    year_gan_tx = TIAN_GAN_TAI_XUAN.get(year_gan, 0)
    month_gan_tx = TIAN_GAN_TAI_XUAN.get(month_gan, 0)
    month_zhi_tx = DI_ZHI_TAI_XUAN.get(month_zhi, 0)
    day_zhi_tx = DI_ZHI_TAI_XUAN.get(day_zhi, 0)
    time_gan_tx = TIAN_GAN_TAI_XUAN.get(time_gan, 0)
    
    return {
        "父亲": D + year_gan_tx,
        "母亲": D + month_gan_tx,
        "兄弟": D + month_zhi_tx,
        "配偶": H + day_zhi_tx,
        "子女": H + time_gan_tx
    }

def calculate_base_number(bazi):
    """计算基础数 BASE：四柱太玄数累加（天干*100 + 地支*10）"""
    year_gan, year_zhi = bazi['year'][0], bazi['year'][1]
    month_gan, month_zhi = bazi['month'][0], bazi['month'][1]
    day_gan, day_zhi = bazi['day'][0], bazi['day'][1]
    time_gan, time_zhi = bazi['time'][0], bazi['time'][1]
    
    year_num = TIAN_GAN_TAI_XUAN.get(year_gan, 0) * 100 + DI_ZHI_TAI_XUAN.get(year_zhi, 0) * 10
    month_num = TIAN_GAN_TAI_XUAN.get(month_gan, 0) * 100 + DI_ZHI_TAI_XUAN.get(month_zhi, 0) * 10
    day_num = TIAN_GAN_TAI_XUAN.get(day_gan, 0) * 100 + DI_ZHI_TAI_XUAN.get(day_zhi, 0) * 10
    time_num = TIAN_GAN_TAI_XUAN.get(time_gan, 0) * 100 + DI_ZHI_TAI_XUAN.get(time_zhi, 0) * 10
    
    base = year_num + month_num + day_num + time_num
    
    return {
        "base": base,
        "year_num": year_num,
        "month_num": month_num,
        "day_num": day_num,
        "time_num": time_num,
        "formula": f"{year_num} + {month_num} + {day_num} + {time_num} = {base}"
    }

def calculate_huangji_total(bazi, dong_gua="巽", xi_gua="乾"):
    """计算皇极玄机总卦策数"""
    year_gan_zhi = bazi['year']
    month_gan_zhi = bazi['month']
    day_gan_zhi = bazi['day']
    time_gan_zhi = bazi['time']
    year_gan = bazi['year'][0]
    
    total = 0
    age_flags = []
    
    for gan_zhi in [year_gan_zhi, month_gan_zhi, day_gan_zhi, time_gan_zhi]:
        data = LIU_SHI_JIA_ZI_DI_LI_CHENG_DING_SHU.get(gan_zhi, {"value": 0, "age": "少"})
        total += data["value"]
        age_flags.append(data["age"])
    
    if "老" in age_flags and "少" in age_flags:
        total += 720
    elif "少" in age_flags and "老" not in age_flags:
        total += 360
    
    total -= NIAN_CHU_SHU.get(year_gan, 0)
    
    total += DONG_GUA_CE_SHU.get(dong_gua, 150)
    total += DONG_GUA_CE_SHU.get(xi_gua, 126)
    
    qian_bai = (total // 100) % 100
    ge_shi = total % 100
    
    qian_bai_sum = (qian_bai // 10) + (qian_bai % 10)
    ge_shi_sum = (ge_shi // 10) + (ge_shi % 10)
    
    if ge_shi_sum > 9:
        ge_shi_sum -= 9
    
    shang_gua = LIAN_SHAN_GUA_SHU.get(qian_bai_sum, "巽")
    xia_gua = LIAN_SHAN_GUA_SHU.get(ge_shi_sum, "乾")
    
    gua_name = shang_gua + xia_gua
    
    return {
        "total": total,
        "qian_bai": qian_bai,
        "ge_shi": ge_shi,
        "qian_bai_sum": qian_bai_sum,
        "ge_shi_sum": ge_shi_sum,
        "shang_gua": shang_gua,
        "xia_gua": xia_gua,
        "huangji_gua": gua_name,
        "age_flags": age_flags,
        "year_gan": year_gan,
        "formula": f"四柱策数 + 老少等 + 动卦策数 - 年除数 = {total}"
    }

def calculate_liuqin_shengxiao_range(bazi):
    """计算六亲生肖范围"""
    year_gan, year_zhi = bazi['year'][0], bazi['year'][1]
    month_gan, month_zhi = bazi['month'][0], bazi['month'][1]
    day_gan, day_zhi = bazi['day'][0], bazi['day'][1]
    time_gan, time_zhi = bazi['time'][0], bazi['time'][1]
    
    liuqin_results = {}
    
    fu_mu_tx = TIAN_GAN_TAI_XUAN.get(year_gan, 0) + DI_ZHI_TAI_XUAN.get(year_zhi, 0)
    fu_mu_sum = fu_mu_tx - 10 if fu_mu_tx > 10 else fu_mu_tx
    liuqin_results["父母"] = {
        "tx_sum": fu_mu_tx,
        "remainder": fu_mu_sum,
        "shengxiao_range": SHENG_XIAO_FAN_WEI.get(fu_mu_sum, [])
    }
    
    xiong_di_tx = TIAN_GAN_TAI_XUAN.get(month_gan, 0) + DI_ZHI_TAI_XUAN.get(month_zhi, 0)
    xiong_di_sum = xiong_di_tx - 10 if xiong_di_tx > 10 else xiong_di_tx
    liuqin_results["兄弟"] = {
        "tx_sum": xiong_di_tx,
        "remainder": xiong_di_sum,
        "shengxiao_range": SHENG_XIAO_FAN_WEI.get(xiong_di_sum, [])
    }
    
    qi_cai_tx = TIAN_GAN_TAI_XUAN.get(day_gan, 0) + DI_ZHI_TAI_XUAN.get(day_zhi, 0)
    qi_cai_sum = qi_cai_tx - 10 if qi_cai_tx > 10 else qi_cai_tx
    liuqin_results["妻财"] = {
        "tx_sum": qi_cai_tx,
        "remainder": qi_cai_sum,
        "shengxiao_range": SHENG_XIAO_FAN_WEI.get(qi_cai_sum, [])
    }
    
    zi_sun_tx = TIAN_GAN_TAI_XUAN.get(time_gan, 0) + DI_ZHI_TAI_XUAN.get(time_zhi, 0)
    zi_sun_sum = zi_sun_tx - 10 if zi_sun_tx > 10 else zi_sun_tx
    liuqin_results["子孙"] = {
        "tx_sum": zi_sun_tx,
        "remainder": zi_sun_sum,
        "shengxiao_range": SHENG_XIAO_FAN_WEI.get(zi_sun_sum, [])
    }
    
    return liuqin_results

def calculate_renyuan_shu(cong_num, year_gan):
    """计算人元数（根据天元数、地元数、世爻五行、动爻五行）"""
    tian_yuan = TIAN_YUAN_SHU.get(year_gan, 1)
    di_yuan = DI_YUAN_SHU.get(cong_num, 1)
    
    A = tian_yuan + di_yuan
    
    shi_yao_wuxing = 3
    dong_yao_wuxing = 3
    B = shi_yao_wuxing + dong_yao_wuxing
    
    if A < 7 and B > 6:
        ren_yuan = (5 * A + B - 11) * 30
    elif A > 6 and B < 7:
        ren_yuan = (5 * A + B - 31) * 30
    elif A < 7 and B < 7:
        ren_yuan = (5 * A + B - 6) * 30
    else:
        ren_yuan = (5 * A + B - 36) * 30
    
    return {
        "tian_yuan": tian_yuan,
        "di_yuan": di_yuan,
        "A": A,
        "shi_yao_wuxing": shi_yao_wuxing,
        "dong_yao_wuxing": dong_yao_wuxing,
        "B": B,
        "renyuan_base": ren_yuan,
        "formula": f"人元数 = ({5 * A} + {B} - {11 if A < 7 and B > 6 else 31 if A > 6 and B < 7 else 6 if A < 7 and B < 7 else 36}) × 30"
    }

def calculate_liuqin_ming_shu(cong_num):
    """计算六亲条文命数"""
    results = {}
    for liuqin, formula in LIU_QIN_MING_SHU_FORMULA.items():
        num = formula(cong_num)
        if num <= 0:
            num += 12
        elif num > 12:
            num -= 12
        results[liuqin] = num
    return results

def calculate_target_number(core, query_topic, secret_table=None):
    """计算目标条文编号：TARGET = CORE + 秘数，循环映射至1~12000"""
    if secret_table is None:
        secret_table = SECRET_NUMBER_TABLE
    
    secret = secret_table.get(query_topic, 0)
    target = core + secret
    
    target = ((target - 1) % 12000) + 1
    
    return {
        "core": core,
        "topic": query_topic,
        "secret": secret,
        "target": target,
        "formula": f"{core} + {secret} = {core + secret} → 循环映射 → {target}"
    }

def get_secret_number(topic, secret_table=None):
    """获取指定事项的秘数"""
    if secret_table is None:
        secret_table = SECRET_NUMBER_TABLE
    return secret_table.get(topic, 0)

def get_secret_topics(secret_table=None):
    """获取所有可用的查询事项"""
    if secret_table is None:
        secret_table = SECRET_NUMBER_TABLE
    return list(secret_table.keys())

def get_tiaowen_by_topic(core, query_topic, fortune_map, secret_table=None):
    """根据核心数和查询事项获取条文"""
    target_info = calculate_target_number(core, query_topic, secret_table)
    target_num = target_info['target']
    
    duanyu, age = "", ""
    if fortune_map and target_num in fortune_map:
        duanyu, age = fortune_map[target_num]
    
    return {
        **target_info,
        "duanyu": duanyu,
        "age": age
    }

__all__ = [
    'get_tai_xuan',
    'get_jiayun',
    'get_day_su',
    'get_hour_su',
    'calculate_liuqinjishu',
    'calculate_base_number',
    'calculate_huangji_total',
    'calculate_liuqin_shengxiao_range',
    'calculate_renyuan_shu',
    'calculate_liuqin_ming_shu',
    'calculate_target_number',
    'get_secret_number',
    'get_secret_topics',
    'get_tiaowen_by_topic',
]
