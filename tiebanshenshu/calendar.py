"""公历到农历及四柱信息的转换。"""
import sys
import datetime as dt

# 尝试导入 cnlunar
try:
    import cnlunar
except ImportError:
    print("【严重错误】: 未找到 'cnlunar' 模块，请运行: pip install cnlunar")
    sys.exit(1)


def convert_to_bazi_info(dt_obj):
    """将公历转为八字信息"""
    try:
        a = cnlunar.Lunar(dt_obj, godType='8char')
        try: lm, ld = int(a.lunarMonth), int(a.lunarDay)
        except: lm, ld = 1, 1 
        return {
            "lunar_month": lm, "lunar_day": ld, "is_leap": "闰" in a.lunarMonthCn,
            "bazi": {"year": a.year8Char, "month": a.month8Char, "day": a.day8Char, "time": a.twohour8Char},
            "date_str": dt_obj.strftime("%Y-%m-%d %H:%M"),
            "lunar_str": f"{a.lunarYearCn}年 {a.lunarMonthCn}{a.lunarDayCn}",
            "hour": dt_obj.hour,
            "minute": dt_obj.minute
        }
    except Exception as e:
        print(f"八字转换失败: {e}")
        return None

def calendar_birth_time(civil):
    """日期输入的23点换日约定；直接输入四柱时不进行此转换。"""
    if civil.hour==23:
        return (civil+dt.timedelta(days=1)).replace(hour=0)
    return civil
