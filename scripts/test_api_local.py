# -*- coding: utf-8 -*-
"""
API 测试 - 本地后端 http://localhost:8070/dgear
"""
import sys, requests, json
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://localhost:8070/dgear"
ISSUES = []

def log(s): print(s, flush=True)

def req(method, path, params=None, data=None, json_body=None,
        desc="", session=None, raw=False):
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
            log(f"          DATA={json.dumps(bdata, ensure_ascii=False)[:500]}")
        if not ok:
            ISSUES.append(dict(method=method, path=path, params=params,
                               status=status, code=code, msg=msg, desc=desc))
        return r, body, bdata
    except Exception as e:
        log(f"  [ERR ] {method:6} {path}  ERROR={e}")
        ISSUES.append(dict(method=method, path=path, params=None,
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
    try:
        r = s.post(BASE + "/auth/login",
                   data={"username": username, "password": password},
                   headers={"Content-Type": "application/x-www-form-urlencoded"},
                   timeout=10)
        body = r.json()
        if body.get("code") == 200:
            token = body["data"]["token"]
            s.headers["Authorization"] = f"Bearer {token}"
            SESSIONS[role] = s
            u = body["data"]["user"]
            log(f"  {role:10} 登录成功 userId={u['userId']} dataScope={u['dataScope']}")
        else:
            log(f"  {role:10} 登录失败: {body}")
    except Exception as e:
        log(f"  {role:10} 错误: {e}")

A = SESSIONS.get("admin")
H = SESSIONS.get("head")
N = SESSIONS.get("nurse")
if not A:
    log("admin 登录失败，终止测试")
    sys.exit(1)

# ── 获取叶子节点 ──────────────────────────────────────────────
_, _, tree_data = req("GET", "/api/indicator/tree", session=A, desc="指标树")
leaf_codes = []
def collect_leaves(node):
    if isinstance(node, list):
        for n in node: collect_leaves(n)
    elif isinstance(node, dict):
        if node.get("isLeaf") == 1:
            c = node.get("metricCode") or node.get("code")
            if c: leaf_codes.append(c)
        for child in node.get("children", []):
            collect_leaves(child)
collect_leaves(tree_data or [])
mc = leaf_codes[0] if leaf_codes else "rate_incision_infection"
log(f"  叶子节点 {len(leaf_codes)} 个，使用 {mc}")

# ── 计算类接口（核心问题）────────────────────────────────────
log("\n" + "="*60)
log(f"计算类接口（叶子节点 {mc}）")
log("="*60)

log("\n-- indicator-item execute --")
for ic in ["a0050", "a0052", "a0106"]:
    req("POST", f"/api/indicator-item/{ic}/execute",
        params={"timeDimension":"MONTH","timeValue":"2025-01"},
        desc=f"execute {ic}", session=A, raw=True)

log("\n-- indicator-result calculate --")
for lc in ([mc] + leaf_codes[1:3]):
    req("POST", "/api/indicator-result/calculate",
        params={"metricCode":lc,"timeDimension":"MONTH","timeValue":"2025-01"},
        desc=f"calculate {lc}", session=A, raw=True)

log("\n-- dept-drill-down --")
for lc in ([mc] + leaf_codes[1:2]):
    req("POST", "/api/indicator-result/dept-drill-down",
        params={"metricCode":lc,"timeDimension":"MONTH","timeValue":"2025-01"},
        desc=f"drill-down {lc}", session=A, raw=True)

# ── 父节点应返回 400 ──────────────────────────────────────────
log("\n-- 父节点 GRP_SURGERY（期望 400）--")
req("POST", "/api/indicator-result/calculate",
    params={"metricCode":"GRP_SURGERY","timeDimension":"MONTH","timeValue":"2025-01"},
    desc="父节点-期望400", session=A, raw=True)

# ── 权限安全 ──────────────────────────────────────────────────
log("\n" + "="*60)
log("权限安全测试")
log("="*60)
for role, s in [("head", H), ("nurse", N)]:
    log(f"\n  -- {role} --")
    req("GET",  "/system/users",    desc=f"{role}访问用户管理", session=s)
    req("DELETE", f"/api/indicator-scope/by-metric/{mc}",
        desc=f"{role}删除scope（破坏性！）", session=s)

# ── 分页 total 字段 ───────────────────────────────────────────
log("\n" + "="*60)
log("分页 total 字段")
log("="*60)
_, _, d = req("GET", "/api/indicator-item/page", params={"page":1,"size":5},
              session=A, raw=True, desc="item分页")
if isinstance(d, dict):
    log(f"  total={d.get('total')} pages={d.get('pages')} records={len(d.get('records',[]))}")

_, _, d = req("GET", "/api/indicator/page", params={"page":1,"size":5},
              session=A, raw=True, desc="indicator分页")
if isinstance(d, dict):
    log(f"  total={d.get('total')} pages={d.get('pages')} records={len(d.get('records',[]))}")

# ── 不存在资源 ────────────────────────────────────────────────
log("\n" + "="*60)
log("不存在资源（期望 404 或 200+null）")
log("="*60)
req("GET", "/api/indicator/99999",       desc="不存在指标", session=A, raw=True)
req("GET", "/api/indicator-item/99999",  desc="不存在指标项", session=A, raw=True)

# ── 异常参数校验 ──────────────────────────────────────────────
log("\n" + "="*60)
log("异常参数（期望 400，不能 500）")
log("="*60)
req("POST", "/api/indicator-result/calculate",
    params={"metricCode":mc,"timeDimension":"MONTH","timeValue":"not-a-date"},
    desc="非法timeValue", session=A, raw=True)
req("POST", "/api/indicator-result/calculate",
    params={"metricCode":mc,"timeDimension":"MONTH"},
    desc="缺少timeValue", session=A, raw=True)
req("POST", "/api/indicator-result/calculate",
    params={"timeDimension":"MONTH","timeValue":"2025-01"},
    desc="缺少metricCode", session=A, raw=True)

# ── 汇总 ─────────────────────────────────────────────────────
log("\n" + "="*60)
log("问题汇总")
log("="*60)
# 401 是预期行为，不算问题
real_issues = [x for x in ISSUES if not (x["status"] == 401 and str(x["code"]) == "401")]
if real_issues:
    log(f"\n  共 {len(real_issues)} 个问题：")
    for i, x in enumerate(real_issues, 1):
        log(f"\n  [{i}] {x['method']} {x['path']}")
        log(f"       desc={x['desc']}")
        log(f"       HTTP={x['status']} code={x['code']} msg={x['msg'][:150]}")
        if x.get("params"):
            log(f"       params={x['params']}")
else:
    log("  无问题！")
