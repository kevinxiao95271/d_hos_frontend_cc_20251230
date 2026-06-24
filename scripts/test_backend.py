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
        with urllib.request.urlopen(req, timeout=10) as r:
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
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode('utf-8', errors='replace'))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode('utf-8', errors='replace')
        try:
            return e.code, json.loads(body_text)
        except:
            return e.code, body_text

def chk(label, status, data, expect_http=200):
    ok = (status == expect_http)
    if isinstance(data, dict) and 'code' in data:
        inner_ok = (data['code'] == 200)
        val = data.get('data')
        inner_code = data['code']
    else:
        inner_ok = True
        val = data
        inner_code = '-'

    if isinstance(val, list):
        summary = 'list[%d]' % len(val)
    elif isinstance(val, dict):
        summary = str(list(val.keys()))[:80]
    else:
        summary = str(val)[:80]

    final_ok = ok and inner_ok
    icon = 'OK  ' if final_ok else 'FAIL'
    print('[%s] %-40s HTTP=%d inner=%s | %s' % (icon, label, status, inner_code, summary))
    return val

def find_leaf(nodes):
    if not isinstance(nodes, list):
        return None
    for n in nodes:
        if isinstance(n, dict):
            if n.get('isLeaf') == 1:
                return n.get('metricCode')
            r = find_leaf(n.get('children', []))
            if r:
                return r
    return None

print('=' * 60)
print('=== 1. 认证模块 ===')
s, d = http_post('/auth/login', params={'username': 'admin', 'password': 'Admin@2026'})
admin_data = chk('admin 登录', s, d)
admin_token = admin_data.get('token') if isinstance(admin_data, dict) else None

s, d = http_post('/auth/login', params={'username': 'neuro_head', 'password': 'Head@2026'})
head_data = chk('neuro_head 登录', s, d)
head_token = head_data.get('token') if isinstance(head_data, dict) else None

s, d = http_post('/auth/login', params={'username': 'neuro_nurse', 'password': 'Nurse@2026'})
nurse_data = chk('neuro_nurse 登录', s, d)
nurse_token = nurse_data.get('token') if isinstance(nurse_data, dict) else None

s, d = http_post('/auth/login', params={'username': 'admin', 'password': 'wrongpass'})
chk('错误密码(应非200)', s, d, expect_http=s)

s, d = http_post('/auth/login', params={'username': 'nobody', 'password': 'x'})
chk('不存在用户(应非200)', s, d, expect_http=s)

if isinstance(admin_data, dict) and isinstance(admin_data.get('user'), dict):
    has_pw = 'password' in admin_data['user']
    label = 'FAIL' if has_pw else 'OK  '
    print('[%s] password字段隐藏 | %s' % (label, '暴露了password!' if has_pw else '未暴露 OK'))

print()
print('=== 2. 菜单接口 ===')
s, d = http_get('/auth/menus', params={'roleId': 1}, token=admin_token)
chk('admin 菜单(roleId=1)', s, d)
s, d = http_get('/auth/menus', params={'roleId': 1})
chk('无token菜单(预期401)', s, d, expect_http=s)

print()
print('=== 3. 用户/科室管理 ===')
s, d = http_get('/system/user/list', token=admin_token)
chk('用户列表', s, d)
s, d = http_get('/system/dept/tree', token=admin_token)
chk('科室树', s, d)
s, d = http_get('/system/dept/list/visible', token=admin_token)
chk('可见科室(admin)', s, d)
s, d = http_get('/system/dept/list/visible', token=head_token)
chk('可见科室(neuro_head)', s, d)
s, d = http_get('/system/user/list')
chk('无token用户列表(预期401)', s, d, expect_http=s)

print()
print('=== 4. 指标管理 ===')
s, d = http_get('/api/indicator/tree', token=admin_token)
tree_val = chk('指标树(admin)', s, d)
s, d = http_get('/api/indicator/tree', token=head_token)
head_tree = chk('指标树(neuro_head)', s, d)
s, d = http_get('/api/indicator/page', params={'current': 1, 'size': 10}, token=admin_token)
chk('指标分页', s, d)
s, d = http_get('/api/indicator/tree')
chk('无token指标树(预期401)', s, d, expect_http=s)

print()
print('=== 5. 指标项管理 ===')
s, d = http_get('/api/indicator-item/list', token=admin_token)
items_val = chk('指标项列表', s, d)
if isinstance(items_val, list) and items_val:
    code0 = items_val[0].get('itemCode')
    print('  第一个itemCode: %s' % code0)
    s, d = http_get('/api/indicator-item/code/' + str(code0), token=admin_token)
    chk('按编码查指标项(%s)' % code0, s, d)

print()
print('=== 6. 指标计算 ===')
s, d = http_get('/api/indicator-result/list', params={'timeDimension': 'YEAR', 'timeValue': '2020'}, token=admin_token)
chk('结果列表(YEAR 2020)', s, d)
s, d = http_get('/api/indicator-result/latest', token=admin_token)
chk('最新结果(admin)', s, d)
s, d = http_get('/api/indicator-result/latest', token=head_token)
chk('最新结果(neuro_head)', s, d)

leaf = find_leaf(tree_val if isinstance(tree_val, list) else [])
print('  叶子指标: %s' % leaf)
if leaf:
    s, d = http_post('/api/indicator-result/calculate',
                     params={'metricCode': leaf, 'timeDimension': 'YEAR',
                             'startDate': '2020-01-01', 'endDate': '2020-12-31'},
                     token=admin_token)
    chk('单指标计算(%s YEAR 2020)' % leaf, s, d)

    s, d = http_post('/api/indicator-result/dept-drill-down',
                     params={'metricCode': leaf, 'timeDimension': 'YEAR',
                             'startDate': '2020-01-01', 'endDate': '2020-12-31'},
                     token=admin_token)
    chk('科室下钻计算(%s)' % leaf, s, d)

    s, d = http_get('/api/indicator-result/dept-drill/' + str(leaf),
                    params={'timeDimension': 'YEAR', 'timeValue': '2020'},
                    token=admin_token)
    chk('查科室下钻结果(%s)' % leaf, s, d)

print()
print('=== 7. 批量计算 ===')
s, d = http_post('/api/indicator-result/batch-calculate',
                 params={'timeDimension': 'YEAR', 'startDate': '2020-01-01', 'endDate': '2020-12-31'},
                 body=[],
                 token=admin_token)
chk('批量计算(全部 YEAR 2020)', s, d)

print()
print('=' * 60)
print('token 长度 admin=%s head=%s nurse=%s' % (
    len(admin_token) if admin_token else 0,
    len(head_token) if head_token else 0,
    len(nurse_token) if nurse_token else 0
))
