# -*- coding: utf-8 -*-
"""
API 测试 v3 - 用正确的叶子节点重测，全面排查剩余问题
"""
import sys, requests, json, time
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://81.71.44.180:8070/dgear"
ISSUES = []  # 真正的问题才进这里

def log(s): print(s, flush=True)

def req(method, path, params=None, data=None, json_body=None,
        desc="", session=None, raw=False, expect_code=200):
    s = session or requests.Session()
    url = BASE + path
    try:
        r = s.request(method, url, params=params, data=data,
                      json=json_body, timeout=20)
        status = r.status_code
        try:
            body = r.json()
            code = body.get("code", "-") if isinstance(body, dict) else "ARRAY"
            msg  = (body.get("message") or body.get("msg") or "") if isinstance(body, dict) else ""
            bdata = body.get("data") if isinstance(body, dict) else body
        except:
            body = r.text[:300]
            code, msg, bdata = "-", str(body), None

        ok = status == 200 and str(code) in ("200", "0", "ARRAY")
        flag = "OK  " if ok else "FAIL"
        log(f"  [{flag}] {method:6} {path}")
        log(f"          HTTP={status} code={code}  {msg[:120]}")
        if raw and bdata is not None:
            log(f"          DATA={json.dumps(bdata, ensure_ascii=False)[:400]}")

        if not ok:
            ISSUES.append(dict(method=method, path=path, params=params,
                               status=status, code=code, msg=msg, desc=desc))
        return r, body, bdata
    except Exception as e:
        log(f"  [ERR ] {method:6} {path}  ERROR={e}")
        ISSUES.append(dict(method=method, path=path, params=params,
                           status="ERR", code="-", msg=str(e), desc=desc))
        return None, None, None

# ── 登录 ─────────────────────────────────────────────────────
log("="*60)
log("登录")
log("="*60)
SESSIONS = {}
for username, password, role in [
    ("admin",       "Admin@123", "admin"),
    ("neuro_head",  "Dept@123",  "head"),
    ("neuro_nurse", "Nurse@123", "nurse"),
]:
    s = requests.Session()
    r = s.post(BASE + "/auth/login",
               data={"username": username, "password": password},
               headers={"Content-Type": "application/x-www-form-urlencoded"},
               timeout=15)
    body = r.json()
    if body.get("code") == 200:
        token = body["data"]["token"]
        s.headers["Authorization"] = f"Bearer {token}"
        SESSIONS[role] = s
        log(f"  {role:10} 登录成功 dataScope={body['data']['user']['dataScope']}")
    else:
        log(f"  {role:10} 登录失败 {body}")

A = SESSIONS["admin"]
H = SESSIONS["head"]
N = SESSIONS["nurse"]

# ── 获取真实叶子指标 ──────────────────────────────────────────
log("\n" + "="*60)
log("获取叶子指标 metricCode（is_leaf=1）")
log("="*60)

_, tree_body, tree_data = req("GET", "/api/indicator/tree", session=A, desc="指标树")
leaf_codes = []
def collect_leaves(node):
    if isinstance(node, list):
        for n in node: collect_leaves(n)
    elif isinstance(node, dict):
        if node.get("isLeaf") == 1 or node.get("is_leaf") == 1 or node.get("leaf") is True:
            c = node.get("metricCode") or node.get("code")
            if c: leaf_codes.append(c)
        for child in node.get("children", []):
            collect_leaves(child)
        # 有些返回 records
        collect_leaves(node.get("records", []))

collect_leaves(tree_data or [])
log(f"  找到叶子节点: {len(leaf_codes)} 个")
if leaf_codes:
    log(f"  前5个: {leaf_codes[:5]}")

# 如果树结构没有 isLeaf 字段，从 page 接口取
if not leaf_codes:
    log("  树未携带 isLeaf，尝试从 page 接口取...")
    _, pg, pg_data = req("GET", "/api/indicator/page",
                         params={"page":1,"size":100,"isLeaf":1},
                         session=A, desc="指标分页-叶子")
    if pg_data:
        records = pg_data.get("records") or pg_data if isinstance(pg_data, list) else []
        for rec in records:
            c = rec.get("metricCode") or rec.get("code")
            if c: leaf_codes.append(c)
    log(f"  从分页得到: {len(leaf_codes)} 个")

# 用已知的叶子节点做兜底
KNOWN_LEAVES = ["rate_incision_infection", "rate_surgery_complication",
                "avg_cost_ami", "avg_cost_csection", "avg_cost_cabg",
                "avg_cost_copd"]
ITEM_CODES    = ["a0050", "a0052", "a0027", "a0029", "a0106"]

mc = leaf_codes[0] if leaf_codes else KNOWN_LEAVES[0]
log(f"  主测 metricCode = {mc}")

# ── 计算类接口重测 ────────────────────────────────────────────
log("\n" + "="*60)
log(f"计算类接口重测（metricCode={mc}）")
log("="*60)

log("\n-- indicator-item execute --")
for ic in ITEM_CODES[:3]:
    req("POST", f"/api/indicator-item/{ic}/execute",
        params={"timeDimension":"MONTH","timeValue":"2025-01"},
        desc=f"execute {ic}", session=A, raw=True)

log("\n-- indicator-result calculate --")
for lc in ([mc] + KNOWN_LEAVES)[:3]:
    req("POST", "/api/indicator-result/calculate",
        params={"metricCode":lc,"timeDimension":"MONTH","timeValue":"2025-01"},
        desc=f"calculate {lc}", session=A, raw=True)

log("\n-- dept-drill-down --")
for lc in ([mc] + KNOWN_LEAVES)[:3]:
    req("POST", "/api/indicator-result/dept-drill-down",
        params={"metricCode":lc,"timeDimension":"MONTH","timeValue":"2025-01"},
        desc=f"drill-down {lc}", session=A, raw=True)

# ── 接口响应格式一致性检查 ───────────────────────────────────
log("\n" + "="*60)
log("响应格式一致性：各接口 data 结构是否符合前端预期")
log("="*60)

log("\n-- /auth/menus 返回结构 --")
req("GET", "/auth/menus", params={"roleId":1}, session=A, raw=True, desc="menus结构")

log("\n-- /system/depts 返回结构 --")
req("GET", "/system/depts", session=A, raw=True, desc="depts结构")

log("\n-- /system/users 返回结构 --")
req("GET", "/system/users", session=A, raw=True, desc="users结构")

log("\n-- /system/roles 返回结构 --")
req("GET", "/system/roles", session=A, raw=True, desc="roles结构")

log("\n-- /api/indicator-item/page 分页结构 --")
_, _, d = req("GET", "/api/indicator-item/page", params={"page":1,"size":3},
              session=A, raw=True, desc="item-page结构")
if d:
    log(f"  分页字段: {list(d.keys()) if isinstance(d, dict) else type(d)}")

log("\n-- /api/indicator/page 分页结构 --")
_, _, d = req("GET", "/api/indicator/page", params={"page":1,"size":3},
              session=A, raw=True, desc="indicator-page结构")
if d:
    log(f"  分页字段: {list(d.keys()) if isinstance(d, dict) else type(d)}")

log("\n-- /api/report/page 分页结构 --")
_, _, d = req("GET", "/api/report/page", params={"page":1,"size":3},
              session=A, raw=True, desc="report-page结构")
if d:
    log(f"  分页字段: {list(d.keys()) if isinstance(d, dict) else type(d)}")

log("\n-- /api/data-entry/page 分页结构 --")
req("GET", "/api/data-entry/page", params={"page":1,"size":3},
    session=A, raw=True, desc="data-entry-page结构")

log("\n-- /api/dataset/page 分页结构 --")
req("GET", "/api/dataset/page", params={"page":1,"size":3},
    session=A, raw=True, desc="dataset-page结构")

# ── 分页参数风格检查：page/size vs pageNum/pageSize ───────────
log("\n" + "="*60)
log("分页参数兼容性：page/size 与 pageNum/pageSize 哪个有效")
log("="*60)
for param_style in [
    {"page":1,"size":5},
    {"pageNum":1,"pageSize":5},
    {"current":1,"size":5},
]:
    _, _, d = req("GET", "/api/indicator-item/page", params=param_style,
                  session=A, desc=f"分页参数{param_style}")
    total = None
    if isinstance(d, dict):
        total = d.get("total") or d.get("totalCount")
        pages = d.get("pages") or d.get("totalPages")
        recs  = len(d.get("records", []))
        log(f"  params={param_style} -> total={total} pages={pages} records={recs}")

# ── dataScope 权限隔离深度验证 ────────────────────────────────
log("\n" + "="*60)
log("dataScope 权限隔离验证（数据是否真的隔离）")
log("="*60)
for role, s in [("admin(50)", A), ("head(70)", H), ("nurse(90)", N)]:
    _, _, d = req("GET", "/api/indicator/page", params={"page":1,"size":100},
                  session=s, desc=f"{role}-indicator-page")
    count = d.get("total") if isinstance(d, dict) else "?"
    log(f"  {role:12} 可见指标数 total={count}")

for role, s in [("admin(50)", A), ("head(70)", H), ("nurse(90)", N)]:
    _, _, d = req("GET", "/api/indicator-result/list",
                  params={"timeDimension":"MONTH","timeValue":"2025-01"},
                  session=s, desc=f"{role}-result-list")
    count = len(d) if isinstance(d, list) else (d.get("total") if isinstance(d, dict) else "?")
    log(f"  {role:12} 可见结果数={count}")

# ── 越权访问测试 ──────────────────────────────────────────────
log("\n" + "="*60)
log("越权测试：低权限用户访问管理接口")
log("="*60)
for role, s in [("head", H), ("nurse", N)]:
    log(f"\n  -- {role} --")
    req("GET",  "/system/users",   desc=f"{role}访问用户管理", session=s)
    req("POST", "/api/indicator",
        json_body={"metricCode":"HACK","metricName":"test"},
        desc=f"{role}创建指标", session=s)
    req("DELETE", "/api/indicator-scope/by-metric/rate_incision_infection",
        desc=f"{role}删除scope", session=s)

# ── 边界值 & 异常参数 ─────────────────────────────────────────
log("\n" + "="*60)
log("边界值 & 异常参数测试")
log("="*60)

log("\n-- 不存在的资源 --")
req("GET",  "/api/indicator/99999",          desc="不存在的指标 id=99999", session=A)
req("GET",  "/api/indicator-item/99999",     desc="不存在的指标项 id=99999", session=A)

log("\n-- 父节点 metricCode 用于计算（期望 400，不能 500）--")
req("POST", "/api/indicator-result/calculate",
    params={"metricCode":"GRP_SURGERY","timeDimension":"MONTH","timeValue":"2025-01"},
    desc="父节点calculate-应400", session=A, raw=True)

log("\n-- 非法时间格式 --")
req("POST", "/api/indicator-result/calculate",
    params={"metricCode":mc,"timeDimension":"MONTH","timeValue":"invalid-date"},
    desc="非法timeValue", session=A, raw=True)
req("POST", "/api/indicator-result/calculate",
    params={"metricCode":mc,"timeDimension":"MONTH"},
    desc="缺少timeValue", session=A, raw=True)
req("POST", "/api/indicator-result/calculate",
    params={"timeDimension":"MONTH","timeValue":"2025-01"},
    desc="缺少metricCode", session=A, raw=True)

log("\n-- XSS / 注入探测（不期望 500）--")
req("GET", "/api/indicator/page",
    params={"page":1,"size":10,"keyword":"<script>alert(1)</script>"},
    desc="XSS探测", session=A)
req("GET", "/api/indicator/page",
    params={"page":1,"size":10,"keyword":"' OR '1'='1"},
    desc="SQL注入探测", session=A)

log("\n-- 超大分页 --")
req("GET", "/api/indicator-item/page",
    params={"page":1,"size":99999},
    desc="size=99999", session=A)

# ── token 失效处理 ────────────────────────────────────────────
log("\n" + "="*60)
log("Token 异常处理")
log("="*60)
bad = requests.Session()
bad.headers["Authorization"] = "Bearer INVALID_TOKEN_12345"
req("GET", "/api/indicator/tree", session=bad, desc="伪造token", raw=True)

expired = requests.Session()
expired.headers["Authorization"] = "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsImRlcHRJZCI6ODIsImRhdGFTY29wZSI6NTAsImV4cCI6MTAwMDAwMDAwMCwidXNlcklkIjozfQ.fake"
req("GET", "/api/indicator/tree", session=expired, desc="过期/篡改token", raw=True)

# ── 汇总 ─────────────────────────────────────────────────────
log("\n" + "="*60)
log("最终问题汇总")
log("="*60)
if ISSUES:
    log(f"\n  共发现 {len(ISSUES)} 个问题：")
    for i, issue in enumerate(ISSUES, 1):
        log(f"\n  [{i}] {issue['method']} {issue['path']}")
        log(f"       desc  = {issue['desc']}")
        log(f"       HTTP  = {issue['status']}  code={issue['code']}")
        log(f"       msg   = {issue['msg'][:150]}")
        if issue.get("params"):
            log(f"       params= {issue['params']}")
else:
    log("  无问题！")
