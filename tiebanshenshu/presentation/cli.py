"""命令行交互入口。"""
import datetime
import traceback
from tiebanshenshu.calendar import convert_to_bazi_info
from tiebanshenshu.engine.calculator import TieBanCalculator


def input_datetime(desc_str):
    """处理用户输入的日期时间"""
    while True:
        try:
            dt_str = input(f"请输入{desc_str} (格式 YYYY-MM-DD HH:MM): ").strip()
            parts = dt_str.split()
            if len(parts) != 2:
                print("格式错误，日期和时间之间请用空格隔开。")
                continue
            date_str, time_str = parts
            year, month, day = map(int, date_str.split('-'))
            hour, minute = map(int, time_str.split(':'))
            if hour >= 23:
                print(f"  [提示] {hour}:{minute} 为晚子时，系统已自动按次日早子时排盘。")
                dt = datetime.datetime(year, month, day) + datetime.timedelta(days=1)
                return datetime.datetime(dt.year, dt.month, dt.day, 0, minute)
            return datetime.datetime(year, month, day, hour, minute)
        except ValueError:
            print("输入无效，请重新输入 (示例: 1951-10-14 18:00)")

def main():
    print("="*60 + "\n  铁板神数排盘系统 (完整版)\n" + "="*60)
    try:
        # 获取性别
        while True:
            g = input("\n请输入性别 (1:男, 2:女): ").strip()
            if g in ['1', '男']:
                gender = "男"
                break
            elif g in ['2', '女']:
                gender = "女"
                break
            else:
                print("输入无效，请输入 1 或 2")

        # 获取时间
        print("\n【时间输入说明】格式为 YYYY-MM-DD HH:MM，例如：1990-01-01 12:00")
        dt_b = input_datetime("出生时间")
        dt_q = input_datetime("求测时间")

        # 转换为八字信息
        print("\n>>> 正在转换八字信息...")
        info_b = convert_to_bazi_info(dt_b)
        info_q = convert_to_bazi_info(dt_q)

        if not info_b:
            print("【错误】出生时间转换失败！")
            return
        if not info_q:
            print("【错误】求测时间转换失败！")
            return

        # 开始排盘
        print("\n>>> 正在进行铁板神数排盘...")
        calculator = TieBanCalculator()
        result = calculator.calculate({
            "birth_info": info_b, 
            "query_info": info_q, 
            "gender": gender
        })

        # 打印报告
        calculator.print_report(result)

        # 保存文件
        calculator.save_to_md(result, info_b['date_str'], info_q['date_str'])

    except KeyboardInterrupt:
        print("\n\n程序已被用户中断")
    except Exception as e:
        print(f"\n\n程序运行出错: {e}")
        traceback.print_exc()
