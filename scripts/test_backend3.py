import urllib.request, json, urllib.parse

BASE = 'http://localhost:8080/dgear'

def http_post(path, params=None, body=None, token=None):
    url = BASE + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else b''
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode('utf-8', errors='replace'))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode('utf-8', errors='replace')
        try:
            return e.code, json.loads(body_text)
        except:
            return e.code, body_text

def http_get(path, params=None, token=None):
    url = BASE + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode('utf-8', errors='replace'))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode('utf-8', errors='replace')
        try:
            return e.code, json.loads(body_text)
        except:
            return e.code, body_text

def login(username, password):
    _, d = http_post('/auth/login', params={'username': username, 'password': password})
    payload = d.get('data', {}) if isinstance(d, dict) and 'data' in d else (d if isinstance(d, dict) else {})
    return payload.get('token'), payload.get('user', {})

def show(label, status, data, expect=None, note=''):
    if isinstance(data, dict) and 'code' in data:
        inner = data['code']
        val   = data.get('data')
        msg   = data.get('message', '')
    else:
        inner = '-'
        val   = data
        msg   = str(data)[:60] if not isinstance(data, (list, dict)) else ''

    if isinstance(val, list):
        summary = 'list[%d]' % len(val)
    elif isinstance(val, dict):
        summary = str(list(val.keys()))[:70]
    elif val is None:
        summary = 'null'
    else:
        summary = str(val)[:70]

    passed = True
    if expect == 401:
        passed = (status == 401)
    elif expect == 'ok':
        passed = (status == 200 and (inner == 200 or inner == '-'))
    elif expect == 'fail':
        passed = (inner != 200 or val is None)

    icon = 'OK  ' if passed else 'FAIL'
    note_str = ' << ' + note if note else ''
    print('[%s] %-48s HTTP=%-3d inner=%-3s | %s%s' % (icon, label, status, inner, summary or msg, note_str))
    return val

admin_token, admin_user = login('admin', 'Admin@123')
head_token,  head_user  = login('neuro_head', 'Dept@123')
nurse_token, nurse_user = login('neuro_nurse', 'Nurse@123')
print('tokens | admin=%s | head deptId=%s scope=%s | nurse deptId=%s scope=%s' % (
    'OK' if admin_token else 'FAIL',
    head_user.get('deptId'), head_user.get('dataScope'),
    nurse_user.get('deptId'), nurse_user.get('dataScope')))
print()

# ============================================================
print('=== 1. 认证 ===')
_, d = http_post('/auth/login', params={'username':'admin','password':'Admin@123'})
show('admin 登录', _, d, 'ok')
_, d = http_post('/auth/login', params={'username':'neuro_head','password':'Dept@123'})
show('neuro_head 登录', _, d, 'ok')
_, d = http_post('/auth/login', params={'username':'neuro_nurse','password':'Nurse@123'})
show('neuro_nurse 登录', _, d, 'ok')
_, d = http_post('/auth/login', params={'username':'admin','password':'wrongpass'})
val = show('错误密码(应非200 data)', _, d, 'fail')
_, d = http_post('/auth/login', params={'username':'nobody','password':'x'})
val = show('不存在用户(应非200 data)', _, d, 'fail')
_, d = http_post('/auth/login', params={'username':'admin','password':'Admin@123'})
user_obj = d.get('data',{}).get('user',{}) if isinstance(d,dict) else {}
pw_exposed = 'password' in user_obj
print('[%s] password字段 | %s' % ('FAIL' if pw_exposed else 'OK  ', '暴露!' if pw_exposed else '未暴露 OK'))

print()
print('=== 2. 菜单（各角色） ===')
for role_id, tok, label in [
    (admin_user.get('roleId',1), admin_token, 'admin'),
    (head_user.get('roleId'), head_token, 'neuro_head'),
    (nurse_user.get('roleId'), nurse_token, 'neuro_nurse'),
]:
    _, d = http_get('/auth/menus', params={'roleId': role_id}, token=tok)
    val = show('菜单 roleId=%s (%s)' % (role_id, label), _, d)
    if isinstance(val, list) and val:
        for m in val:
            print('  └ %s | path=%s' % (m.get('menuName','?'), m.get('path','?')))
_, d = http_get('/auth/menus', params={'roleId':1})
show('无token菜单(预期401)', _, d, 401)

print()
print('=== 3. 科室 / 用户 ===')
_, d = http_get('/system/dept/tree', token=admin_token)
show('科室树', _, d, 'ok')
_, d = http_get('/system/dept/list/visible', token=admin_token)
show('可见科室(admin)', _, d, 'ok')
_, d = http_get('/system/dept/list/visible', token=head_token)
head_depts = show('可见科室(neuro_head)', _, d, 'ok')
_, d = http_get('/system/dept/list/visible', token=nurse_token)
nurse_depts = show('可见科室(neuro_nurse)', _, d, 'ok')
_, d = http_get('/system/user/list', token=admin_token)
show('用户列表', _, d, 'ok')
_, d = http_get('/system/user/list')
show('无token用户列表(预期401)', _, d, 401)
if isinstance(head_depts, list):
    print('  head可见: %s' % [x.get('deptName') for x in head_depts])
if isinstance(nurse_depts, list):
    print('  nurse可见: %s' % [x.get('deptName') for x in nurse_depts])

print()
print('=== 4. 指标树 + 权限隔离 ===')
_, d = http_get('/api/indicator/tree', token=admin_token)
admin_tree = show('指标树(admin)', _, d, 'ok')
_, d = http_get('/api/indicator/tree', token=head_token)
head_tree = show('指标树(neuro_head)', _, d, 'ok')
_, d = http_get('/api/indicator/tree', token=nurse_token)
nurse_tree = show('指标树(neuro_nurse)', _, d, 'ok')
_, d = http_get('/api/indicator/tree')
show('无token指标树(预期401)', _, d, 401)

def find_all_leaves(nodes, result=None):
    if result is None: result = []
    if not isinstance(nodes, list): return result
    for n in nodes:
        if isinstance(n, dict):
            if n.get('isLeaf') == 1:
                result.append(n.get('metricCode'))
            find_all_leaves(n.get('children', []), result)
    return result

admin_leaves = find_all_leaves(admin_tree if isinstance(admin_tree, list) else [])
head_leaves  = find_all_leaves(head_tree  if isinstance(head_tree,  list) else [])
nurse_leaves = find_all_leaves(nurse_tree if isinstance(nurse_tree, list) else [])
print('  叶子指标: admin=%d head=%d nurse=%d' % (len(admin_leaves), len(head_leaves), len(nurse_leaves)))
leaf = admin_leaves[0] if admin_leaves else '10.3.1'

print()
print('=== 5. 指标项 + 执行 ===')
_, d = http_get('/api/indicator-item/list', token=admin_token)
items = show('指标项列表', _, d, 'ok')
if isinstance(items, list):
    for item in items[:3]:
        ic = item.get('itemCode')
        _, d = http_post('/api/indicator-item/%s/execute' % ic,
                         params={'startDate':'2020-01-01','endDate':'2020-12-31'}, token=admin_token)
        v = show('执行指标项 %s' % ic, _, d, 'ok')
        if isinstance(v, dict):
            print('  success=%s result=%s err=%s' % (v.get('success'), str(v.get('result',''))[:50], v.get('errorMessage')))

print()
print('=== 6. validate-sql ===')
for label, sql in [
    ('合法SQL', 'SELECT COUNT(*) AS result_value FROM d_mr WHERE 1=1'),
    ('危险SQL-DROP', 'DROP TABLE d_mr'),
    ('表不存在', 'SELECT COUNT(*) FROM no_such_table_xyz'),
    ('语法错误', 'SELEC * FORM d_mr'),
]:
    _, d = http_post('/api/indicator-item/validate-sql', body=sql, token=admin_token)
    v = show('validate-sql: %s' % label, _, d)
    if isinstance(v, dict):
        print('  valid=%s msg=%s' % (v.get('valid'), v.get('message','')))
    elif v is not None:
        print('  返回: %s' % str(v)[:80])

print()
print('=== 7. validate-expression ===')
for label, expr in [
    ('合法表达式', 'a0050 + a0052'),
    ('除零', 'a0050 / 0'),
    ('非法字符', 'A001 ### BAD'),
]:
    _, d = http_post('/api/indicator/validate-expression', body=expr, token=admin_token)
    v = show('validate-expr: %s' % label, _, d)
    if isinstance(v, dict):
        print('  valid=%s msg=%s' % (v.get('valid'), v.get('message','')))
    elif v is not None:
        print('  返回: %s' % str(v)[:80])

print()
print('=== 8. 时间维度全覆盖 ===')
for dim, tv, sd, ed in [
    ('YEAR',    '2020',      '2020-01-01', '2020-12-31'),
    ('QUARTER', '2020-Q1',   '2020-01-01', '2020-03-31'),
    ('MONTH',   '2020-01',   '2020-01-01', '2020-01-31'),
    ('DAY',     '2020-01-01','2020-01-01', '2020-01-01'),
]:
    s, d = http_post('/api/indicator-result/calculate',
                     params={'metricCode':leaf,'timeDimension':dim,'startDate':sd,'endDate':ed},
                     token=admin_token)
    show('计算 %s (%s)' % (dim, leaf), s, d, 'ok')
    s, d = http_get('/api/indicator-result/list',
                    params={'timeDimension':dim,'timeValue':tv}, token=admin_token)
    v = show('查询 %s timeValue=%s' % (dim, tv), s, d, 'ok')
    if isinstance(v, list) and v:
        print('  timeValue存储值=%s' % v[0].get('timeValue'))

print()
print('=== 9. 科室下钻 ===')
s, d = http_post('/api/indicator-result/dept-drill-down',
                 params={'metricCode':leaf,'timeDimension':'YEAR','startDate':'2020-01-01','endDate':'2020-12-31'},
                 token=admin_token)
show('科室下钻-计算(%s)' % leaf, s, d, 'ok')
s, d = http_get('/api/indicator-result/dept-drill/%s' % leaf,
                params={'timeDimension':'YEAR','timeValue':'2020'}, token=admin_token)
drill = show('科室下钻-查询(%s)' % leaf, s, d, 'ok')
if isinstance(drill, list) and drill:
    print('  首条: deptName=%s value=%s' % (drill[0].get('deptName'), drill[0].get('resultValue')))
    print('  共%d个科室' % len(drill))

print()
print('=== 10. latest权限对比 ===')
_, da = http_get('/api/indicator-result/latest', token=admin_token)
admin_l = show('latest(admin)', _, da, 'ok')
_, dh = http_get('/api/indicator-result/latest', token=head_token)
head_l  = show('latest(neuro_head)', _, dh, 'ok')
_, dn = http_get('/api/indicator-result/latest', token=nurse_token)
nurse_l = show('latest(neuro_nurse)', _, dn, 'ok')
if isinstance(admin_l,list) and isinstance(head_l,list):
    a_codes = set(r.get('metricCode') for r in admin_l)
    h_codes = set(r.get('metricCode') for r in head_l)
    diff = a_codes - h_codes
    print('  admin有但head没有: %s' % (diff or '无差异<<权限未隔离 FAIL'))

print()
print('=== 11. 边界/异常 ===')
_, d = http_get('/api/indicator/code/NOTEXIST', token=admin_token)
show('查不存在指标', _, d)
_, d = http_get('/api/indicator-item/code/NOTEXIST', token=admin_token)
show('查不存在指标项', _, d)
s, d = http_post('/api/indicator-result/calculate',
                 params={'metricCode':'NOTEXIST','timeDimension':'YEAR','startDate':'2020-01-01','endDate':'2020-12-31'},
                 token=admin_token)
v = show('计算不存在指标(应报错)', s, d)
print('  返回: code=%s msg=%s' % (d.get('code') if isinstance(d,dict) else '?', d.get('message','') if isinstance(d,dict) else str(d)[:60]))
s, d = http_post('/api/indicator-result/calculate',
                 params={'metricCode':leaf,'timeDimension':'YEAR','startDate':'2020/01/01','endDate':'2020/12/31'},
                 token=admin_token)
v2 = show('计算 日期格式斜杠(应报错)', s, d)
print('  返回: code=%s msg=%s' % (d.get('code') if isinstance(d,dict) else '?', d.get('message','') if isinstance(d,dict) else str(d)[:60]))
s, d = http_post('/api/indicator-result/calculate',
                 params={'metricCode':leaf},
                 token=admin_token)
show('计算 缺timeDimension(应报错)', s, d)
_, d = http_get('/api/indicator/tree', token='fake.token.here')
show('伪造token(预期401)', _, d, 401)

print()
print('=' * 60)
print('done.')
