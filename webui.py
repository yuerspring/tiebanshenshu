"""只提供视频计算流程的网页服务。"""
import datetime as dt
import os
import re
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge
from tiebanshenshu.calendar import convert_to_bazi_info, calendar_birth_time
from tiebanshenshu.methods.video import VideoMethodCalculator
from tiebanshenshu.methods.video_corpus import load_comparison_verses

app=Flask(__name__)
app.config.update(MAX_CONTENT_LENGTH=4096)

def error(message,status=400):
    return jsonify(success=False,error={'code':'INVALID_INPUT' if status<500 else 'CALCULATION_FAILED','message':message}),status

@app.after_request
def response_headers(response):
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='no-referrer'
    response.headers['X-Frame-Options']='DENY'
    response.headers['X-App-Edition']='video-only'
    if request.path.startswith('/api/'):
        response.headers['Cache-Control']='no-store'
    return response

@app.errorhandler(RequestEntityTooLarge)
def too_large(exc):
    return error('输入内容过长',413)

@app.get('/')
def index():
    return render_template('video.html')

@app.get('/api/v1/health')
def health():
    try:
        loaded=bool(load_comparison_verses())
    except Exception:
        app.logger.exception('Verse loading failed')
        loaded=False
    return jsonify(success=loaded,edition='video-only',engine='zefang_video_o3mkGBcPkrI',
                   revision=os.environ.get('RENDER_GIT_COMMIT','local'),database_loaded=loaded),200 if loaded else 503

@app.post('/api/v1/video-chart')
def calculate():
    data=request.get_json(silent=True)
    if not isinstance(data,dict):
        return error('请填写出生日期或四柱')
    allowed={'bazi','birth_date','birth_time','basis_number','fortune_pillar','known_parents'}
    if set(data)-allowed:
        return error('仅支持视频演算输入')
    try:
        if 'bazi' in data:
            bazi=data['bazi'];basis='caller_supplied_pillars'
        else:
            date,time=data.get('birth_date'),data.get('birth_time')
            if not isinstance(date,str) or not isinstance(time,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',date) or not re.fullmatch(r'\d{2}:\d{2}',time):
                raise ValueError('请填写有效日期和时刻')
            civil=dt.datetime.strptime(f'{date} {time}','%Y-%m-%d %H:%M')
            if not 1900<=civil.year<=2099:
                raise ValueError('出生年份须在1900至2099之间；其他年份请直接填写四柱')
            info=convert_to_bazi_info(calendar_birth_time(civil))
            if not info:
                raise ValueError('日期转换失败，请直接填写四柱')
            bazi=info['bazi'];basis='civil_calendar_conversion'
        result=VideoMethodCalculator(load_comparison_verses()).calculate(
            bazi,basis_number=data.get('basis_number'),fortune_pillar=data.get('fortune_pillar'),
            known_parents=data.get('known_parents'))
        result['input_basis']=basis
        return jsonify(success=True,data=result)
    except (ValueError,TypeError) as exc:
        return error(str(exc))
    except Exception:
        app.logger.exception('Video calculation failed')
        return error('演算失败，请稍后重试',500)

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT','7860')),debug=False)
