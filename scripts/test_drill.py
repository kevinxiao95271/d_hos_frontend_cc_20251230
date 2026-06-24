import urllib.request, json, urllib.parse
BASE = 'http://localhost:8080/dgear'

def req(method, path, params=None, body=None, token=None):
    url = BASE + path
    if params: url += '?' + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else (b'' if method in ('POST','DELETE') else None)
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header('Content-Type', 'application/json')
    if token: r.add_header('Authorization', 'Bearer ' + token)
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            raw = resp.read().decode('utf-8', errors='replace')
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8', errors='replace')
        try: return e.code, json.loads(raw)
        except: return e.code, raw

_, d = req('POST', '/auth/login', params={'username':'admin','password':'Admin@123'})
token = d.get('data',{}).get('token')

_, d = req('GET', '/api/indicator/page', params={'current':1,'size':200}, token=token)
records = d.get('data',{}).get('records',[])
drill_leaves = [r for r in records if r.get('isLeaf')==1 and r.get('supportDeptDrill')==1]
all_leaves   = [r for r in records if r.get('isLeaf')==1]
targets = drill_leaves if drill_leaves else all_leaves

print('下钻叶子指标: ' + str([l['metricCode'] for l in targets]))
print()

dims = [
    ('YEAR',    '2020-01-01', '2020-12-31', '2020'),
    ('QUARTER', '2020-01-01', '2020-03-31', '2020Q1'),
    ('MONTH',   '2020-03-01', '2020-03-31', '2020-03'),
    ('DAY',     '2020-03-15', '2020-03-15', '2020-03-15'),
]

for leaf in targets[:2]:
    code = leaf['metricCode']
    name = leaf.get('metricName','')
    print('=' * 55)
    print('指标: ' + code + ' | ' + name)
    print('=' * 55)

    for dim, sd, ed, tv in dims:
        print('  -- ' + dim + ' --')

        # Step1
        s, d = req('POST', '/api/indicator-result/calculate',
                   params={'metricCode':code,'timeDimension':dim,'startDate':sd,'endDate':ed},
                   token=token)
        val = d.get('data') if isinstance(d,dict) else None
        rv = val.get('resultValue') if isinstance(val,dict) else val
        print('  Step1 calculate: HTTP=' + str(s) + ' code=' + str(d.get('code') if isinstance(d,dict) else '?') + ' resultValue=' + str(rv))

        # Step2
        s, d = req('POST', '/api/indicator-result/dept-drill-down',
                   params={'metricCode':code,'timeDimension':dim,'startDate':sd,'endDate':ed},
                   token=token)
        val = d.get('data') if isinstance(d,dict) else None
        msg = d.get('message','') if isinstance(d,dict) else str(d)[:80]
        dept_count = len(val) if isinstance(val,list) else '?'
        nonzero = len([x for x in val if x.get('resultValue',0) != 0]) if isinstance(val,list) else 0
        print('  Step2 drill-down: HTTP=' + str(s) + ' depts=' + str(dept_count) + ' nonzero=' + str(nonzero) + ' msg=' + msg[:60])
        if isinstance(val, list):
            for item in val[:3]:
                print('    ' + str(item.get('deptName','?')) + ' => ' + str(item.get('resultValue')))

        # Step3
        s, d = req('GET', '/api/indicator-result/dept-drill/' + code,
                   params={'timeDimension':dim,'timeValue':tv}, token=token)
        val = d.get('data') if isinstance(d,dict) else None
        cached = len(val) if isinstance(val,list) else val
        ok_label = 'OK' if isinstance(val,list) and len(val) > 0 else 'EMPTY'
        print('  Step3 GET cached: HTTP=' + str(s) + ' count=' + str(cached) + ' [' + ok_label + ']')
        print()
