"""Mobile web adapter around the original V2 calculation entrypoint."""
import datetime as dt
import json
import logging
import os
import traceback
from flask import Flask, jsonify, render_template, request
from main import TieBanCalculator, convert_to_bazi_info

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
calculator = None
logger = logging.getLogger(__name__)
ANIMALS = set('鼠牛虎兔龙蛇马羊猴鸡狗猪')
KIN = {'父亲', '母亲', '兄弟', '配偶', '子女'}


def init_calculator():
    global calculator
    if calculator is None:
        calculator = TieBanCalculator()
    return calculator


def error(code, message, status=400):
    return jsonify({'success': False, 'error': {'code': code, 'message': message}}), status


def input_datetime(data, name):
    date_text, time_text = data.get(f'{name}_date'), data.get(f'{name}_time')
    if not isinstance(date_text, str) or not isinstance(time_text, str):
        raise ValueError('请填写完整的出生时间和求测时间')
    return dt.datetime.strptime(f'{date_text} {time_text}', '%Y-%m-%d %H:%M')


def compute_chart(data):
    """Use V2 TieBanCalculator.calculate exactly once for a request."""
    gender = data['gender']
    birth = input_datetime(data, 'birth')
    query = input_datetime(data, 'query')
    if birth > query:
        raise ValueError('出生时间不能晚于求测时间')
    entered_birth = birth.strftime('%Y-%m-%d %H:%M')
    # Match V2's webui.py and main.py treatment of late 子时; keep minutes.
    if birth.hour >= 23:
        birth = (birth + dt.timedelta(days=1)).replace(hour=0)
    birth_info = convert_to_bazi_info(birth)
    query_info = convert_to_bazi_info(query)
    if not birth_info or not query_info:
        raise ValueError('农历或八字转换失败，请检查日期')
    payload = {'gender': gender, 'birth_info': birth_info, 'query_info': query_info}
    supplied = data.get('known_shengxiao') or {}
    # The V2 engine reads only the first item. Keep the selection independent of JSON key ordering.
    known = {key: supplied[key] for key in ('父亲', '母亲', '兄弟', '配偶', '子女') if key in supplied}
    if known:
        payload['known_shengxiao'] = known
    result = init_calculator().calculate(payload)
    verification = result.get('keke', {}).get('kao_ke_info') or {}
    validation = {
        'provided_relations': list(known),
        'used_relation': verification.get('liuqin_type'),
        'matches': verification.get('match_count', 0),
        'birth_destiny_affected_by_zodiac': False,
        'note': 'V2 仅用第一个已知六亲生肖筛选八刻；本命兄弟条文和秘数表不随生肖考刻改变。',
    }
    destiny = []
    table = result.get('tbl_data')
    if table:
        for topic, offsets in table['offsets'].items():
            for offset in offsets:
                number = table['base'] + table['seq'] + offset
                sentence, age = init_calculator().get_fortune_duanyu(number)
                destiny.append({'topic': topic, 'number': number, 'sentence': sentence, 'age': age,
                                'base': table['base'], 'sequence': table['seq'], 'offset': offset,
                                'formula': f"{table['base']}+{table['seq']}+{offset}={number}"})
    return json.loads(json.dumps({
        'input_birth': entered_birth, 'input_query': query.strftime('%Y-%m-%d %H:%M'),
        'birth_info': birth_info, 'query_info': query_info, 'gender': gender,
        'destiny_articles': destiny, 'result': result, 'validation': validation,
    }, ensure_ascii=False, default=str))


@app.after_request
def response_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/api/v1/health')
def health():
    return jsonify({'success': True, 'engine': 'TiebanshenshuOS_V2', 'database_loaded': bool(init_calculator().db.FORTUNE_DUANYU_MAP)})


@app.post('/api/v1/chart')
@app.post('/api/calculate')
def api_calculate():
    if request.content_length and request.content_length > 4096:
        return error('INVALID_INPUT', '输入内容过长', 413)
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or data.get('gender') not in ('男', '女'):
        return error('INVALID_INPUT', '请选择性别并填写日期时间')
    known = data.get('known_shengxiao') or {}
    if not isinstance(known, dict) or any(k not in KIN or v not in ANIMALS for k, v in known.items()):
        return error('INVALID_INPUT', '考刻验证生肖填写有误')
    try:
        return jsonify({'success': True, 'data': compute_chart(data)})
    except ValueError as exc:
        return error('INVALID_DATETIME', str(exc))
    except Exception:
        logger.error('V2 calculation failed\n%s', traceback.format_exc())
        return error('CALCULATION_FAILED', '计算失败，请检查输入后重试', 500)


if __name__ == '__main__':
    init_calculator()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '7860')), debug=False)
