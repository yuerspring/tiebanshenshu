"""No formula is duplicated here: calculation runs the original class."""
from main import TieBanCalculator
from .lunar import lunar_info, parse_original_datetime


class ChartService:
    def __init__(self, loader):
        self.calculator = TieBanCalculator(loader)

    def calculate(self, gender: str, birth_datetime: str, query_datetime: str):
        birth_dt = parse_original_datetime(birth_datetime)
        query_dt = parse_original_datetime(query_datetime)
        if birth_dt > query_dt:
            raise ValueError("出生时间不能晚于求测时间")
        birth = lunar_info(birth_dt)
        query = lunar_info(query_dt)
        original = self.calculator.calculate({
            "birth_info": birth, "query_info": query, "gender": gender,
        })
        if len(original["liunian"]) != 108:
            raise RuntimeError("流年计算未完成")
        basic = {
            "gender": gender,
            "birth_datetime": birth["date_str"],
            "birth_datetime_input": birth_datetime,
            "birth_lunar": birth["lunar_str"],
            "birth_is_leap": birth["is_leap"],
            "birth_bazi": birth["bazi"],
            "query_datetime": query["date_str"],
            "query_datetime_input": query_datetime,
            "query_bazi": query["bazi"],
        }
        chart = {
            "cong_num": original["cong_num"],
            "cong_calc": original["cong_calc"],
            "tone_num": original["tone_num"],
            "day_life": int(original["day_life_calc"].split("日命:")[1].split(",")[0]),
            "time_luck": int(original["day_life_calc"].split("时运:")[1]),
            "day_life_calc": original["day_life_calc"],
            "moment": original["moment_cn"],
            "moment_calc": original["moment_calc"],
            "main_num": original["main_num"],
            "main_calc": original["main_calc"],
            "hexagram": original["hex_name"],
            "later_num": original["pn_num"],
            "later_calc": original["pn_log"],
        }
        articles = []
        if original["tbl_data"]:
            tbl = original["tbl_data"]
            for item, offsets in tbl["offsets"].items():
                for offset in offsets:
                    number = tbl["base"] + tbl["seq"] + offset
                    sentence, age = self.calculator.get_fortune_duanyu(number)
                    articles.append({
                        "item": item, "number": number,
                        "base": tbl["base"], "sequence": tbl["seq"], "offset": offset,
                        "formula": f"{tbl['base']} + {tbl['seq']} + {offset} = {number}",
                        "duanyu": sentence, "duanyu_age": age,
                        "source": "14-10.csv；铁板神数-条文断词.csv",
                    })
        return {
            "basic_info": basic, "basic_chart": chart,
            "destiny_articles": articles,
            "destiny_source": original["tbl_data"],
            "annual_fortunes": [dict(item) for item in original["liunian"] if item["age"] <= 100],
            "original_fields": original,
        }
