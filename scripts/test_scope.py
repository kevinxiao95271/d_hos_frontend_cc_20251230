import urllib.request, json, urllib.parse

BASE = 'http://localhost:8080/dgear'

def req(method, path, params=None, body=None, token=None):
    url = BASE + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else (b'' if method in ('POST','DELETE') else None)
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header('Content-Type', 'application/json')
    if token:
        r.add_header('Authorization', 'Bearer ' + token)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            raw = resp.read().decode('utf-8', errors='replace')
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8', errors='replace')
        try: return e.code, json.loads(raw)
        except: return e.code, raw

def show(label, s, d):
    if isinstance(d, dict) and 'code' in d:
        ok = d['code'] == 200
        val = d.get('data')
        msg = d.get('message', '')
    else:
        ok = (s == 200)
        val = d
        msg = ''
    if isinstance(val, list): summary = 'list[%d]' % len(val)
    elif isinstance(val, dict): summary = str(list(val.keys()))[:60]
    elif val is None: summary = 'null'
    else: summary = str(val)[:80]
    print('[%s] %-52s HTTP=%d | %s' % ('OK  ' if ok else 'FAIL', label, s, summary or msg))
    return val

# 登录
def login(u, p):
    _, d = req('POST', '/auth/login', params={'username': u, 'password': p})
    pl = d.get('data', d) if isinstance(d, dict) else {}
    return pl.get('token'), pl.get('user', {})

admin_token, admin_user = login('admin', 'Admin@123')
head_token,  head_user  = login('neuro_head', 'Dept@123')
print('登录 admin=%s head deptId=%s' % ('OK' if admin_token else 'FAIL', head_user.get('deptId')))
print()

HEAD_DEPT = head_user.get('deptId', 1)
TEST_METRICS = ['10.3.1', '10.3.2']

print('=== 1. 基础查询（操作前） ===')
s, d = req('GET', '/api/indicator-scope/by-dept/%s' % HEAD_DEPT, token=admin_token)
before_bindings = show('by-dept/%s 绑定列表(操作前)' % HEAD_DEPT, s, d)

s, d = req('GET', '/api/indicator-scope/by-metric/10.3.1', token=admin_token)
show('by-metric/10.3.1 绑定科室(操作前)', s, d)

print()
print('=== 2. 新增单条绑定 ===')
s, d = req('POST', '/api/indicator-scope/binding',
           body={'deptId': HEAD_DEPT, 'metricCode': '10.3.2.1', 'isPrimaryOwner': 1},
           token=admin_token)
show('POST binding deptId=%s metricCode=10.3.2.1' % HEAD_DEPT, s, d)

# 幂等测试：重复提交
s, d = req('POST', '/api/indicator-scope/binding',
           body={'deptId': HEAD_DEPT, 'metricCode': '10.3.2.1', 'isPrimaryOwner': 1},
           token=admin_token)
show('POST binding 重复提交(应幂等)', s, d)

print()
print('=== 3. 批量覆盖（replace-by-dept） ===')
s, d = req('POST', '/api/indicator-scope/replace-by-dept',
           body={'deptId': HEAD_DEPT, 'metricCodes': TEST_METRICS, 'isPrimaryOwner': 1},
           token=admin_token)
show('replace-by-dept deptId=%s codes=%s' % (HEAD_DEPT, TEST_METRICS), s, d)

# 验证覆盖结果
s, d = req('GET', '/api/indicator-scope/by-dept/%s' % HEAD_DEPT, token=admin_token)
after_replace = show('by-dept/%s 绑定列表(覆盖后)' % HEAD_DEPT, s, d)
if isinstance(after_replace, list):
    codes = [x.get('metricCode') for x in after_replace]
    print('  绑定指标: %s' % codes)
    extra = [c for c in codes if c not in TEST_METRICS]
    print('  覆盖是否生效(10.3.2.1应消失): %s' % ('OK' if '10.3.2.1' not in codes else 'FAIL-旧绑定未清除'))

print()
print('=== 4. 权限生效验证 ===')
# 用 head token 查 latest，应只看到 TEST_METRICS 里的
s, d = req('GET', '/api/indicator-result/latest', token=head_token)
latest = show('neuro_head latest(绑定%s后)' % TEST_METRICS, s, d)
if isinstance(latest, list):
    codes = set(r.get('metricCode') for r in latest)
    print('  head latest指标集: %s' % sorted(codes))
    unexpected = codes - set(TEST_METRICS)
    print('  权限过滤: %s' % ('OK 仅返回绑定指标' if not unexpected else 'WARN 额外指标=%s' % unexpected))

print()
print('=== 5. replace-by-metric ===')
s, d = req('POST', '/api/indicator-scope/replace-by-metric',
           body={'metricCode': '10.3.1', 'deptIds': [HEAD_DEPT], 'isPrimaryOwner': 1},
           token=admin_token)
show('replace-by-metric 10.3.1 deptIds=[%s]' % HEAD_DEPT, s, d)

s, d = req('GET', '/api/indicator-scope/by-metric/10.3.1', token=admin_token)
v = show('by-metric/10.3.1 绑定科室(replace后)', s, d)
if isinstance(v, list):
    print('  绑定科室: %s' % [x.get('deptId') for x in v])

print()
print('=== 6. 删除单条绑定 ===')
s, d = req('DELETE', '/api/indicator-scope/binding',
           params={'deptId': HEAD_DEPT, 'metricCode': '10.3.2'},
           token=admin_token)
show('DELETE binding deptId=%s metricCode=10.3.2' % HEAD_DEPT, s, d)

s, d = req('GET', '/api/indicator-scope/by-dept/%s' % HEAD_DEPT, token=admin_token)
after_del = show('by-dept/%s(删单条后)' % HEAD_DEPT, s, d)
if isinstance(after_del, list):
    print('  剩余绑定: %s' % [x.get('metricCode') for x in after_del])

print()
print('=== 7. 清空操作 ===')
s, d = req('DELETE', '/api/indicator-scope/by-dept/%s' % HEAD_DEPT, token=admin_token)
show('DELETE by-dept/%s 清空' % HEAD_DEPT, s, d)

s, d = req('GET', '/api/indicator-scope/by-dept/%s' % HEAD_DEPT, token=admin_token)
after_clear = show('by-dept/%s(清空后，应为空)' % HEAD_DEPT, s, d)
if isinstance(after_clear, list):
    print('  清空结果: %s' % ('OK list[0]' if len(after_clear) == 0 else 'FAIL 仍有%d条' % len(after_clear)))

print()
print('=== 8. 恢复初始绑定 ===')
s, d = req('POST', '/api/indicator-scope/replace-by-dept',
           body={'deptId': HEAD_DEPT, 'metricCodes': ['10.3.1', '10.3.2'], 'isPrimaryOwner': 1},
           token=admin_token)
show('恢复 neuro_head 绑定 10.3.1+10.3.2', s, d)

print()
print('=== 9. 无权限操作（head token 尝试修改） ===')
s, d = req('POST', '/api/indicator-scope/binding',
           body={'deptId': HEAD_DEPT, 'metricCode': '10.3.2.2', 'isPrimaryOwner': 0},
           token=head_token)
show('head token 调 binding(应403或拒绝)', s, d)

print()
print('done.')
