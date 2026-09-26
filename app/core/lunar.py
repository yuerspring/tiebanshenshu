"""Input adapter that preserves main.py's 23:00 rollover and cnlunar conversion."""
from datetime import datetime, timedelta
from main import convert_to_bazi_info


def parse_original_datetime(value: str):
    # Same transformation as main.input_datetime; use a strict API representation.
    try:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError as exc:
        raise ValueError("日期时间无效，请按 YYYY-MM-DD HH:MM 填写") from exc
    if dt.strftime("%Y-%m-%d %H:%M") != value:
        raise ValueError("日期时间格式不正确")
    if dt.hour >= 23:
        dt = datetime(dt.year, dt.month, dt.day) + timedelta(days=1)
        return dt.replace(minute=int(value[-2:]))
    return dt


def lunar_info(dt: datetime):
    result = convert_to_bazi_info(dt)
    if result is None:
        raise RuntimeError("农历和八字转换失败")
    return result
