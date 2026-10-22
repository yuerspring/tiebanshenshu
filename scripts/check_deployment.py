"""Run video-example regressions against an explicitly supplied deployment URL."""
import argparse
import json
from pathlib import Path
import urllib.error
import urllib.request

EXAMPLE={'year':'乙巳','month':'辛巳','day':'甲申','time':'丙子'}
PAYLOAD={'bazi':EXAMPLE,'basis_number':9003,'fortune_pillar':'壬午','known_parents':{'父亲':'鼠','母亲':'牛'}}

def run(base_url,revision=None):
    checks=[]
    def check(name,actual,expected,source='contract'):
        checks.append({'name':name,'passed':actual==expected,'actual':actual,'expected':expected,'source':source})
    def request(path,payload=None,raw=None):
        body=raw if raw is not None else json.dumps(payload).encode() if payload is not None else None
        req=urllib.request.Request(base_url.rstrip('/')+path,data=body,headers={'Content-Type':'application/json','User-Agent':'video-regression/1.0'})
        try:
            with urllib.request.urlopen(req,timeout=120) as response:
                return response.status,response.read().decode(),{k.lower():v for k,v in response.headers.items()}
        except urllib.error.HTTPError as exc:return exc.code,exc.read().decode(),{k.lower():v for k,v in exc.headers.items()}
    status,text,headers=request('/api/v1/health');health=json.loads(text)
    check('health',status,200);check('video-only edition',health.get('edition'),'video-only')
    if revision:check('deployed revision',health.get('revision'),revision)
    status,page,_=request('/');check('homepage',status,200)
    check('minimal example button','视频例子' in page,True)
    check('no retired UI',any(s in page for s in ('OS对照','十四表','/legacy','benming-number','video-conflicts')),False)
    status,text,headers=request('/api/v1/video-chart',PAYLOAD)
    check('video request',status,200);r=json.loads(text)['data']
    check('private calculation response',headers.get('cache-control'),'no-store')
    k=r['preliminary']
    check('Taixuan total',k['sum'],55,'video_shown')
    check('ke remainder',k['remainder'],0,'video_shown')
    check('initial ke',k['initial_ke_candidate'],1,'video_shown')
    check('second kaoke number',k['base_number'],9467,'video_shown')
    check('1327 multipliers',[a['multiplier'] for a in k['secret_candidates']],[0,1,2,4,6,8,10,12,14],'video_rule')
    check('year/month jiaze',[x['jiaze']['number'] for x in r['pillar_articles'][:2]],[2381,4381],'video_shown')
    check('year/month sums',[x['stem_branch_sum_number'] for x in r['pillar_articles'][:2]],[3345,3945],'video_shown')
    check('four pillar jiaze',[x['jiaze']['number'] for x in r['pillar_articles']],[2381,4381,6382,8389],'video_rule_derivation')
    check('four pillar sums',[x['stem_branch_sum_number'] for x in r['pillar_articles']],[3345,3945,3942,4226],'video_rule_derivation')
    check('parent bases',[p['base_number'] for p in r['parent_candidates']],[9003,9655],'video_shown')
    n=r['number_method'];check('9003 pair sums',n['pair_sums'],[9,3],'video_shown')
    check('9003 hexagram',[n['upper'],n['lower']],['坎','震'],'video_shown')
    check('derived jiaze basis',n['number'],1387,'video_rule_derivation')
    check('arithmetic makes no factual confirmation',n['input_fact_verified'],False)
    check('annual original example',r['annual']['number'],6476,'video_shown')
    before=r['before_after']['before'];after=r['before_after']['after']
    check('before combination',before['combination'],3467,'video_rule_derivation')
    check('continuous before sequence',[a['number'] for a in before['articles']],[4950,5046,5142,5238],'contextual_derivation')
    check('after combination',after['combination'],8831,'contextual_derivation')
    check('continuous after sequence',[a['number'] for a in after['articles']],[10122,10026,9930,9834],'contextual_derivation')
    check('life cycle length',len(r['life_sequence']['articles']),125,'video_rule_derivation')
    check('no duplicate life numbers',len(set(a['number'] for a in r['life_sequence']['articles'])),125)
    check('eight video tables',len(r['reference_tables']),8,'video_shown')
    for number in (5003,9655):
        status,text,_=request('/api/v1/video-chart',{**PAYLOAD,'basis_number':number})
        check(f'{number} fallback response',status,200)
        check(f'{number} four-stem fallback',json.loads(text)['data']['number_method']['number'],9126,'video_rule')
    status,text,_=request('/api/v1/video-chart',{**PAYLOAD,'bazi':dict(EXAMPLE,time='己亥')})
    check('center-five response',status,200);special=json.loads(text)['data']
    check('center-five only pauses after',special['before_after']['after']['status'],'requires_middle_five_rule')
    check('center-five keeps before',special['before_after']['before']['status'],'calculated')
    for path in ['/legacy','/api/v1/chart','/api/calculate','/api/v1/time-audit','/api/v1/time-sensitivity','/api/v1/compare-os','/api/v1/legacy/chart','/api/legacy/calculate','/api/v1/legacy/time-audit','/api/v1/legacy/time-sensitivity','/api/v1/legacy/compare-os','/static/js/app.js']:
        check('removed '+path,request(path)[0],404)
    for path in ['/static/js/video.js','/static/css/style.css']:check('asset '+path,request(path)[0],200)
    for key,value in [('basis_number',True),('known_parents',[]),('fortune_pillar',[]),('confirmed_number',9003)]:
        check('reject invalid '+key,request('/api/v1/video-chart',{**PAYLOAD,key:value})[0],400)
    check('body size limit',request('/api/v1/video-chart',raw=b'x'*5000)[0],413)
    _,text,_=request('/api/v1/video-chart',PAYLOAD)
    check('repeat is deterministic',json.loads(text)['data']==r,True)
    def date_request(date,time):
        status,text,_=request('/api/v1/video-chart',{'birth_date':date,'birth_time':time})
        check('calendar '+date+' '+time,status,200)
        return json.loads(text)['data']
    late=date_request('1991-03-02','23:15');early=date_request('1991-03-03','00:15')
    check('late-Zi consistent pillars',late['bazi'],early['bazi'])
    return {'url':base_url,'revision':health.get('revision'),'passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url');parser.add_argument('--revision');parser.add_argument('--report',type=Path)
    args=parser.parse_args();result=run(args.url,args.revision)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False))
    for check in result['checks']:
        if not check['passed']:print(json.dumps(check,ensure_ascii=False))
    raise SystemExit(0 if result['passed'] else 1)

if __name__=='__main__':main()
