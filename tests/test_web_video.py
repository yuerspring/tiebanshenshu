"""Video-only web boundary and source-removal regression checks."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from webui import app

ROOT=Path(__file__).resolve().parents[1]
EXAMPLE={'year':'乙巳','month':'辛巳','day':'甲申','time':'丙子'}
PAYLOAD={'bazi':EXAMPLE,'basis_number':9003,'fortune_pillar':'壬午','known_parents':{'父亲':'鼠','母亲':'牛'}}

class VideoWebTests(unittest.TestCase):
    def setUp(self):self.client=app.test_client()

    def test_full_video_example(self):
        response=self.client.post('/api/v1/video-chart',json=PAYLOAD)
        self.assertEqual(response.status_code,200)
        r=response.json['data']
        self.assertEqual(r['preliminary']['sum'],55)
        self.assertEqual(r['preliminary']['base_number'],9467)
        self.assertEqual([p['jiaze']['number'] for p in r['pillar_articles']],[2381,4381,6382,8389])
        self.assertEqual([p['stem_branch_sum_number'] for p in r['pillar_articles']],[3345,3945,3942,4226])
        self.assertEqual(r['number_method']['number'],1387)
        self.assertEqual([a['number'] for a in r['before_after']['before']['articles']],[4950,5046,5142,5238])
        self.assertEqual([a['number'] for a in r['before_after']['after']['articles']],[10122,10026,9930,9834])
        self.assertEqual(r['annual']['number'],6476)
        self.assertEqual([p['base_number'] for p in r['parent_candidates']],[9003,9655])
        self.assertEqual(response.headers['Cache-Control'],'no-store')
        self.assertEqual(response.headers['X-App-Edition'],'video-only')

    def test_all_retired_endpoints_and_assets_are_gone(self):
        paths=['/legacy','/api/v1/chart','/api/calculate','/api/v1/time-audit','/api/v1/time-sensitivity','/api/v1/compare-os','/api/v1/legacy/chart','/api/legacy/calculate','/api/v1/legacy/time-audit','/api/v1/legacy/time-sensitivity','/api/v1/legacy/compare-os']
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code,404)
                self.assertEqual(self.client.post(path,json=PAYLOAD).status_code,404)
        self.assertEqual(self.client.get('/static/js/app.js').status_code,404)
        for relative in ['reference_os','reference_adapter.py','keke_module.py','time_rules.py','templates/index.html','tiebanshenshu/engine','tiebanshenshu/kaoke','tiebanshenshu/tables','tiebanshenshu/data']:
            self.assertFalse((ROOT/relative).exists(),relative)
        self.assertEqual(sorted(p.name for p in (ROOT/'DB').glob('*')),['List.csv'])

    def test_invalid_payloads_are_bounded_json_errors(self):
        cases=[None,[],True,{}, {'bazi':{}},{'bazi':dict(EXAMPLE,day='甲')},
               {**PAYLOAD,'basis_number':True},{**PAYLOAD,'basis_number':9003.5},
               {**PAYLOAD,'basis_number':'9003'}, {**PAYLOAD,'basis_number':0},
               {**PAYLOAD,'basis_number':13000},{**PAYLOAD,'known_parents':[]},
               {**PAYLOAD,'known_parents':{'父亲':'猫'}},{**PAYLOAD,'fortune_pillar':[]},
               {**PAYLOAD,'confirmed_number':9003},{**PAYLOAD,'benming_gua_number':2000}]
        for payload in cases:
            with self.subTest(payload=payload):
                r=self.client.post('/api/v1/video-chart',data=json.dumps(payload),content_type='application/json')
                self.assertEqual(r.status_code,400,r.json)
                self.assertEqual(r.json['error']['code'],'INVALID_INPUT')
        for date,time in [('2024-02-30','12:00'),('1899-01-01','12:00'),('2100-01-01','12:00'),('2024-01-01','25:00'),('2024-1-1','12:00')]:
            self.assertEqual(self.client.post('/api/v1/video-chart',json={'birth_date':date,'birth_time':time}).status_code,400)

    def test_request_limits_and_error_privacy(self):
        r=self.client.post('/api/v1/video-chart',data='x'*5000,content_type='application/json')
        self.assertEqual(r.status_code,413)
        self.assertTrue(r.is_json)
        with patch('webui.VideoMethodCalculator.calculate',side_effect=RuntimeError('internal-secret')):
            with self.assertLogs(app.logger,level='ERROR'):
                r=self.client.post('/api/v1/video-chart',json=PAYLOAD)
            self.assertEqual(r.status_code,500)
            self.assertNotIn('internal-secret',r.get_data(as_text=True))

    def test_health_requires_corpus_and_identifies_edition(self):
        r=self.client.get('/api/v1/health')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json['edition'],'video-only')
        with patch('webui.load_comparison_verses',return_value={}):
            self.assertEqual(self.client.get('/api/v1/health').status_code,503)

    def test_calendar_late_zi_and_direct_pillars(self):
        def request(date,time):return self.client.post('/api/v1/video-chart',json={'birth_date':date,'birth_time':time}).json['data']
        late=request('1991-03-02','23:15');early=request('1991-03-03','00:15')
        self.assertEqual(late['bazi'],early['bazi'])
        self.assertEqual(late['input_basis'],'civil_calendar_conversion')
        direct=self.client.post('/api/v1/video-chart',json={'bazi':late['bazi']}).json['data']
        self.assertEqual(late['pillar_articles'],direct['pillar_articles'])

    def test_minimal_page_and_static_assets(self):
        page=self.client.get('/').get_data(as_text=True)
        self.assertIn('视频例子',page)
        for text in ['十四表','OS对照','历史版','本命数覆盖','benming-number','number-confirmed','video-conflicts']:
            self.assertNotIn(text,page)
        self.assertEqual(self.client.get('/static/js/video.js').status_code,200)
        self.assertEqual(self.client.get('/static/css/style.css').status_code,200)

    def test_cli_uses_the_same_continuous_example(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'video.json'
            proc=subprocess.run([sys.executable,'-m','tiebanshenshu','--pillars','乙巳','辛巳','甲申','丙子','--basis-number','9003','--fortune-pillar','壬午','--output',str(path)],cwd=ROOT,capture_output=True,text=True,timeout=30)
            self.assertEqual(proc.returncode,0,proc.stderr)
            r=json.loads(path.read_text())
            self.assertEqual(r['number_method']['number'],1387)
            self.assertEqual(r['annual']['number'],6476)

if __name__=='__main__':unittest.main()
