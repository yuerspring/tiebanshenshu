import re
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.server import app
from app.services.report_service import render_markdown

BASE = Path(__file__).parent / "baselines"
CASES = [
    ("readme", "男", "1924-06-15 16:00", "2025-04-20 10:00"),
    ("late_zi_female", "女", "1990-02-03 23:45", "2025-07-07 23:30"),
    ("female", "女", "1988-05-18 07:20", "2026-09-26 11:00"),
]


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def fields_from_markdown(text):
    fields = {}
    for line in text.splitlines():
        if line.startswith("- "):
            key, _, value = line[2:].partition("：")
            fields[key] = value
    rows = [line for line in text.splitlines() if re.match(r"^\| \d+ \|", line)]
    return fields, rows


@pytest.mark.parametrize("name,gender,birth,query", CASES)
def test_web_matches_original_cli(client, name, gender, birth, query):
    payload = {"gender": gender, "birth_datetime": birth, "query_datetime": query}
    response = client.post("/api/v1/chart", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    base = (BASE / f"{name}.md").read_text(encoding="utf-8")
    base_fields, base_rows = fields_from_markdown(base)
    basic = data["basic_chart"]
    assert basic["cong_calc"] == base_fields["先天命数"]
    assert str(basic["tone_num"]) == base_fields["五音命数"]
    assert basic["day_life_calc"] == base_fields["日命数 & 时运数"]
    assert basic["moment_calc"] == base_fields["考刻结果"]
    assert basic["main_calc"] == base_fields["本命数"]
    assert basic["hexagram"] == base_fields["十二辟卦"]
    assert len(data["annual_fortunes"]) == len(base_rows) == 100
    assert len(data["original_fields"]["liunian"]) == 108
    timestamp = re.search(r"\*\*排盘时间\*\*: ([\d :\-]+)", base).group(1)
    report = render_markdown(data, datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"))
    assert report == base
    assert data["annual_fortunes"][0]["age"] == 1
    assert data["annual_fortunes"][-1]["age"] == 100
    old = (BASE / "before_14_10_fix" / f"{name}.md").read_text(encoding="utf-8")
    old_fields, old_rows = fields_from_markdown(old)
    assert base_fields == old_fields, "14-10 表头修复不应改变核心命数"
    assert base_rows == old_rows, "14-10 表头修复不应改变流年结果"


def test_readme_exact_values(client):
    response = client.post("/api/v1/chart", json={"gender":"男", "birth_datetime":"1924-06-15 16:00", "query_datetime":"2025-04-20 10:00"})
    data = response.json()["data"]
    assert data["basic_chart"]["cong_num"] == 11
    assert data["basic_chart"]["tone_num"] == 2
    assert data["basic_chart"]["day_life"] == 4
    assert data["basic_chart"]["time_luck"] == 3
    assert data["basic_chart"]["moment"] == "初刻"
    assert data["basic_chart"]["main_num"] == 344
    assert data["basic_chart"]["hexagram"] == "泰"
    assert [(a["item"], a["number"]) for a in data["destiny_articles"]] == [
        ("性格", 9760), ("性格", 1353), ("财运", 10606), ("兄弟个数", 1559)
    ]
    assert data["destiny_articles"][0]["duanyu"] == "水火性情发则焚，燎原静则渊潮平。"
    assert data["annual_fortunes"][35]["corrected_fortune"] == "7273"


def test_late_zi_and_original_destiny_loader(client):
    response = client.post("/api/v1/chart", json={
        "gender":"女", "birth_datetime":"1990-02-03 23:45", "query_datetime":"2025-07-07 23:30"
    })
    info = response.json()["data"]["basic_info"]
    assert info["birth_datetime"] == "1990-02-04 00:45"
    assert info["query_datetime"] == "2025-07-08 00:30"
    loader = client.app.state.service.calculator.loader
    assert len(loader.DESTINY_DATA) == 288
    offsets = [entry["base"] + entry["seq"] + offset
               for entry in loader.DESTINY_DATA.values()
               for values in entry["offsets"].values() for offset in values]
    assert len(offsets) == 1422
    assert all(number in loader.FORTUNE_DUANYU_MAP for number in offsets)


def test_validation_and_pages(client):
    assert client.get("/api/v1/health").json()["data"]["database_loaded"]
    assert client.get("/").status_code == 200
    assert client.get("/result").status_code == 200
    assert client.get("/about").status_code == 200
    assert client.get("/static/app.js").status_code == 200
    base = {"gender": "女", "birth_datetime": "2025-06-01 12:00", "query_datetime": "2025-05-01 12:00"}
    bad = client.post("/api/v1/chart", json=base)
    assert bad.status_code == 422
    assert bad.json()["error"]["code"] == "INVALID_DATETIME"
    assert client.post("/api/v1/chart", json={**base,"gender":"invalid"}).status_code == 422
    assert client.post("/api/v1/chart", json={**base,"csv_path":"/etc/passwd"}).status_code == 422
    assert client.post("/api/v1/chart", content="not json").status_code == 400
    assert "Traceback" not in bad.text


def test_export_does_not_persist(client):
    response = client.post("/api/v1/report.md", json={"gender":"男", "birth_datetime":"1924-06-15 16:00", "query_datetime":"2025-04-20 10:00"})
    assert response.status_code == 200
    assert "| 100 |" in response.text
    assert "attachment" in response.headers["content-disposition"]
