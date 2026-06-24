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

def ok(label, status, data, note=''):
    if isinstance(data, dict) and 'code' in data:
        icon = 'OK  ' if data['code'] == 200 else 'FAIL'
        val = data.get('data')
        msg = data.get('message','')
    else:
        icon = 'OK  ' if status == 200 else 'INFO'
        val = data
        msg = ''
    if isinstance(val, list):
        summary = 'list[%d]' % len(val)
    elif isinstance(val, dict):
        summary = str(list(val.keys()))[:60]
    else:
        summary = str(val)[:80]
    note_str = (' << ' + note) if note else ''
    print('[%s] %-45s HTTP=%d | %s%s' % (icon, label, status, summary or msg, note_str))
    return val

# ---- 登录拿 token ----
def login(username, password):
    _, d = http_post('/auth/login', params={'username': username, 'password': password})
    # 响应结构: {code:200, data:{token:..., user:{...}}}
    payload = d.get('data', {}) if isinstance(d, dict) and 'data' in d else (d if isinstance(d, dict) else {})
    return payload.get('token'), payload.get('user', {})

admin_token, admin_user = login('admin', 'Admin@123')
head_token,  head_user  = login('neuro_head', 'Dept@123')
nurse_token, nurse_user = login('neuro_nurse', 'Nurse@123')
print('tokens OK | head deptId=%s dataScope=%s | nurse deptId=%s dataScope=%s' % (
    head_user.get('deptId'), head_user.get('dataScope'),
    nurse_user.get('deptId'), nurse_user.get('dataScope')))
print()

# ---- A. 菜单 各角色 ----
print('=== A. 各角色菜单 ===')
_, d = http_get('/auth/menus', params={'roleId':1}, token=admin_token)
menus_admin = ok('菜单 roleId=1(超管)', _, d)
_, d = http_get('/auth/menus', params={'roleId': head_user.get('roleId',2)}, token=head_token)
menus_head = ok('菜单 roleId=%s(head)' % head_user.get('roleId'), _, d)
_, d = http_get('/auth/menus', params={'roleId': nurse_user.get('roleId',3)}, token=nurse_token)
menus_nurse = ok('菜单 roleId=%s(nurse)' % nurse_user.get('roleId'), _, d)
if isinstance(menus_admin, list):
    for m in menus_admin:
        print('  admin菜单:', m.get('menuName','?'), '| path:', m.get('path','?'), '| children:', len(m.get('children',[])))

print()
# ---- B. 科室树 结构探查 ----
print('=== B. 科室结构 ===')
_, d = http_get('/system/dept/tree', token=admin_token)
tree_val = ok('科室树(全量)', _, d)
_, d = http_get('/system/dept/list/visible', token=head_token)
head_depts = ok('head可见科室', _, d)
_, d = http_get('/system/dept/list/visible', token=nurse_token)
nurse_depts = ok('nurse可见科室', _, d)
# 科室树顶层
if isinstance(tree_val, list):
    for dept in tree_val[:3]:
        print('  顶层科室: id=%s name=%s children=%d' % (dept.get('deptId'), dept.get('deptName'), len(dept.get('children',[]))))
if isinstance(head_depts, list):
    for dept in head_depts[:5]:
        print('  head可见: id=%s name=%s' % (dept.get('deptId'), dept.get('deptName')))
if isinstance(nurse_depts, list):
    for dept in nurse_depts[:5]:
        print('  nurse可见: id=%s name=%s' % (dept.get('deptId'), dept.get('deptName')))

print()
# ---- C. 指标树 详细结构 ----
print('=== C. 指标树结构 ===')
_, d = http_get('/api/indicator/tree', token=admin_token)
tree_admin = ok('指标树(admin全量)', _, d)
_, d = http_get('/api/indicator/tree', params={'metricPool':'POOL_NATIONAL'}, token=admin_token)
ok('指标树 POOL_NATIONAL', _, d)

def find_all_leaves(nodes, result=None):
    if result is None: result = []
    if not isinstance(nodes, list): return result
    for n in nodes:
        if isinstance(n, dict):
            if n.get('isLeaf') == 1:
                result.append({'code': n.get('metricCode'), 'name': n.get('metricName'), 'type': n.get('metricType')})
            find_all_leaves(n.get('children', []), result)
    return result

leaves = find_all_leaves(tree_admin if isinstance(tree_admin, list) else [])
print('  全部叶子指标(%d个):' % len(leaves))
for lf in leaves:
    print('    %s | %s | type=%s' % (lf['code'], lf['name'], lf['type']))

print()
# ---- D. 权限隔离深挖 ----
print('=== D. 权限隔离深挖 ===')
_, d = http_get('/api/indicator/tree', token=head_token)
head_tree = ok('指标树(neuro_head)', _, d)
head_leaves = find_all_leaves(head_tree if isinstance(head_tree, list) else [])
print('  head可见叶子: %d个' % len(head_leaves))

_, d = http_get('/api/indicator/tree', token=nurse_token)
nurse_tree = ok('指标树(neuro_nurse)', _, d)
nurse_leaves = find_all_leaves(nurse_tree if isinstance(nurse_tree, list) else [])
print('  nurse可见叶子: %d个' % len(nurse_leaves))

# latest 对比
_, da = http_get('/api/indicator-result/latest', token=admin_token)
admin_latest = ok('latest结果(admin)', _, da)
_, dh = http_get('/api/indicator-result/latest', token=head_token)
head_latest = ok('latest结果(head)', _, dh)
_, dn = http_get('/api/indicator-result/latest', token=nurse_token)
nurse_latest = ok('latest结果(nurse)', _, dn)

if isinstance(admin_latest, list) and isinstance(head_latest, list):
    admin_codes = set(r.get('metricCode') for r in admin_latest)
    head_codes = set(r.get('metricCode') for r in head_latest)
    diff = admin_codes - head_codes
    print('  admin有但head没有的指标结果: %s' % (diff or '无差异 <<权限未隔离'))

print()
# ---- E. 时间维度全覆盖 ----
print('=== E. 时间维度全覆盖 ===')
leaf_code = leaves[0]['code'] if leaves else '10.3.1'
for dim, tv, sd, ed in [
    ('YEAR',    '2020', '2020-01-01', '2020-12-31'),
    ('QUARTER', '2020Q1', '2020-01-01', '2020-03-31'),
    ('MONTH',   '2020-01', '2020-01-01', '2020-01-31'),
    ('DAY',     '2020-01-01', '2020-01-01', '2020-01-01'),
]:
    s, d = http_post('/api/indicator-result/calculate',
                     params={'metricCode': leaf_code, 'timeDimension': dim,
                             'startDate': sd, 'endDate': ed},
                     token=admin_token)
    ok('计算 %s(%s)' % (dim, leaf_code), s, d)
    s, d = http_get('/api/indicator-result/list',
                    params={'timeDimension': dim, 'timeValue': tv},
                    token=admin_token)
    ok('查询 %s timeValue=%s' % (dim, tv), s, d)

print()
# ---- F. SQL/表达式校验 ----
print('=== F. SQL / 表达式校验 ===')
_, d = http_post('/api/indicator-item/validate-sql', body='SELECT COUNT(*) AS result_value FROM d_mr', token=admin_token)
ok('validate-sql (合法)', _, d)
_, d = http_post('/api/indicator-item/validate-sql', body='DROP TABLE d_mr', token=admin_token)
ok('validate-sql (危险SQL)', _, d)
_, d = http_post('/api/indicator-item/validate-sql', body='SELECT * FROM nonexist_table', token=admin_token)
ok('validate-sql (表不存在)', _, d)
_, d = http_post('/api/indicator/validate-expression', body='A001 + A002', token=admin_token)
ok('validate-expression (合法)', _, d)
_, d = http_post('/api/indicator/validate-expression', body='A001 / 0', token=admin_token)
ok('validate-expression (除零)', _, d)
_, d = http_post('/api/indicator/validate-expression', body='INVALID###', token=admin_token)
ok('validate-expression (非法)', _, d)

print()
# ---- G. 指标项执行 ----
print('=== G. 指标项立即执行 ===')
_, items_d = http_get('/api/indicator-item/list', token=admin_token)
items_list = items_d if isinstance(items_d, list) else (items_d.get('data',[]) if isinstance(items_d,dict) else [])
# unwrap if needed
if not isinstance(items_list, list):
    items_list = []
for item in items_list[:3]:
    ic = item.get('itemCode')
    s, d = http_post('/api/indicator-item/%s/execute' % ic,
                     params={'startDate':'2020-01-01','endDate':'2020-12-31'},
                     token=admin_token)
    ok('执行指标项 %s' % ic, s, d)

print()
# ---- H. 边界 / 异常情况 ----
print('=== H. 边界与异常 ===')
# 不存在的指标
_, d = http_get('/api/indicator/code/NOTEXIST', token=admin_token)
ok('查不存在指标', _, d)
# 不存在的指标项
_, d = http_get('/api/indicator-item/code/NOTEXIST', token=admin_token)
ok('查不存在指标项', _, d)
# 计算不存在指标
s, d = http_post('/api/indicator-result/calculate',
                 params={'metricCode':'NOTEXIST','timeDimension':'YEAR','startDate':'2020-01-01','endDate':'2020-12-31'},
                 token=admin_token)
ok('计算不存在指标', s, d)
# 日期格式错误
s, d = http_post('/api/indicator-result/calculate',
                 params={'metricCode': leaf_code, 'timeDimension':'YEAR','startDate':'2020/01/01','endDate':'2020/12/31'},
                 token=admin_token)
ok('计算 日期格式错误(斜杠)', s, d)
# 缺少必填参数
s, d = http_post('/api/indicator-result/calculate',
                 params={'metricCode': leaf_code},
                 token=admin_token)
ok('计算 缺少timeDimension', s, d)
# 过期/伪造token
s, d = http_get('/api/indicator/tree', token='fake.token.here')
ok('伪造token(预期401)', s, d, note='应401')

print()
print('done.')
