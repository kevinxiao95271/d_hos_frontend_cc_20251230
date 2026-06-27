# -*- coding: utf-8 -*-
"""
后端 API 测试 v2 - 按最新后端说明重测
登录: POST /auth/login  Content-Type: application/x-www-form-urlencoded
"""
import sys, requests, json
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://81.71.44.180:8070/dgear"
RESULTS = []

def log(s): print(s, flush=True)

def req(method, path, params=None, data=None, json_body=None,
        headers=None, desc="", session=None, raw=False):
    s = session or requests.Session()
    url = BASE + path
    try:
        r = s.request(method, url, params=params, data=data,
                      json=json_body, headers=headers, timeout=15)
        status = r.status_code
        try:
            body = r.json()
            code = body.get("code", "-") if isinstance(body, dict) else "ARRAY"
            msg  = (body.get("message") or body.get("msg") or "") if isinstance(body, dict) else ""
        except:
            body = r.text[:200]
            code, msg = "-", str(body)
        ok = status == 200 and str(code) in ("200","0","ARRAY")
        flag = "OK  " if ok else "FAIL"
        log(f"  [{flag}] {method:6} {path}")
        log(f"          HTTP={status} code={code}  {msg[:100]}")
        if raw:
            log(f"          RAW={json.dumps(body, ensure_ascii=False)[:500]}")
        RESULTS.append(dict(method=method, path=path, status=status,
                            code=code, msg=msg, desc=desc, ok=ok))
        return r, body
    except Exception as e:
        log(f"  [ERR ] {method:6} {path}  ERROR={e}")
        RESULTS.append(dict(method=method, path=path, status="ERR",
                            code="-", msg=str(e), desc=desc, ok=False))
        return None, None

# ── Swagger ──────────────────────────────────────────────────
log("="*60)
log("STEP 1: Swagger / 公开路径")
log("="*60)
for p in ["/v3/api-docs", "/swagger-ui/index.html", "/swagger-ui.html",
          "/swagger-resources", "/doc.html"]:
    try:
        r = requests.get(BASE + p, timeout=8)
        log(f"  {p:40} -> HTTP {r.status_code}")
    except Exception as e:
        log(f"  {p:40} -> ERROR {e}")

# ── 登录三个账号 ──────────────────────────────────────────────
log("\n" + "="*60)
log("STEP 2: 登录（form-urlencoded）")
log("="*60)

SESSIONS = {}

for username, password, role in [
    ("admin",       "Admin@123", "超级管理员"),
    ("neuro_head",  "Dept@123",  "科室主任"),
    ("neuro_nurse", "Nurse@123", "普通科室人员"),
]:
    s = requests.Session()
    try:
        r = s.post(
            BASE + "/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15
        )
        body = r.json()
        log(f"\n  [{role}] {username} / {password}")
        log(f"    HTTP={r.status_code} code={body.get('code')} msg={body.get('message','')}")
        if body.get("code") == 200:
            d = body.get("data", {})
            token = d.get("token") if isinstance(d, dict) else None
            user  = d.get("user",  {}) if isinstance(d, dict) else {}
            log(f"    登录成功 userId={user.get('userId')} dataScope={user.get('dataScope')}")
            if token:
                s.headers["Authorization"] = f"Bearer {token}"
                SESSIONS[role] = s
        else:
            log(f"    登录失败 RAW={json.dumps(body, ensure_ascii=False)[:300]}")
    except Exception as e:
        log(f"    ERROR={e}")

# 选主测 session
main_s = SESSIONS.get("超级管理员") or requests.Session()

# ── 用户/认证模块 ─────────────────────────────────────────────
log("\n" + "="*60)
log("STEP 3: 用户 / 认证模块")
log("="*60)
req("GET",  "/auth/userInfo",          desc="当前用户信息",   session=main_s, raw=True)
req("GET",  "/auth/menus",             desc="菜单列表",
    params={"roleId":1},               session=main_s, raw=True)
req("GET",  "/system/users",           desc="用户管理列表",   session=main_s)
req("GET",  "/system/roles",           desc="角色列表",       session=main_s)
req("GET",  "/system/depts",           desc="科室列表",       session=main_s)

# ── 指标项 ────────────────────────────────────────────────────
log("\n" + "="*60)
log("STEP 4: 指标项模块")
log("="*60)
req("GET",  "/api/indicator-item/list",  desc="指标项列表",     session=main_s)
req("GET",  "/api/indicator-item/page",  desc="指标项分页",
    params={"page":1,"size":5},          session=main_s, raw=True)
req("GET",  "/api/indicator-item/1",     desc="指标项详情 id=1",session=main_s, raw=True)

# 拿真实 itemCode 再测执行
log("\n  -- 尝试获取真实指标项 code --")
r, body = req("GET", "/api/indicator-item/list", session=main_s, desc="_内部")
item_code = None
if body and isinstance(body, dict) and body.get("data"):
    items = body["data"]
    if isinstance(items, list) and items:
        item_code = items[0].get("itemCode") or items[0].get("code") or "1"
        log(f"  使用 itemCode={item_code}")

req("POST", f"/api/indicator-item/{item_code or '1'}/execute",
    params={"timeDimension":"MONTH","timeValue":"2025-01"},
    desc="执行指标项", session=main_s, raw=True)

# ── 指标 ──────────────────────────────────────────────────────
log("\n" + "="*60)
log("STEP 5: 指标模块")
log("="*60)
req("GET",  "/api/indicator/tree",     desc="指标树",         session=main_s)
req("GET",  "/api/indicator/page",     desc="指标分页",
    params={"page":1,"size":5},        session=main_s)
req("GET",  "/api/indicator/1",        desc="指标详情 id=1",  session=main_s)

# ── 指标计算结果 ──────────────────────────────────────────────
log("\n" + "="*60)
log("STEP 6: 指标计算结果")
log("="*60)
# 先拿真实 metricCode
r, body = req("GET", "/api/indicator/tree", session=main_s, desc="_内部")
metric_code = None
if body and isinstance(body, dict) and body.get("data"):
    def find_code(node):
        if isinstance(node, dict):
            c = node.get("metricCode") or node.get("code")
            if c: return c
            for child in node.get("children", []):
                r = find_code(child)
                if r: return r
        elif isinstance(node, list):
            for n in node:
                r = find_code(n)
                if r: return r
        return None
    metric_code = find_code(body["data"])
    if metric_code:
        log(f"  使用 metricCode={metric_code}")

mc = metric_code or "TEST"
req("POST", "/api/indicator-result/calculate",
    params={"metricCode":mc,"timeDimension":"MONTH","timeValue":"2025-01"},
    desc="单指标计算", session=main_s, raw=True)
req("GET",  "/api/indicator-result/list",
    params={"metricCode":mc,"timeDimension":"MONTH","timeValue":"2025-01"},
    desc="指标结果列表", session=main_s)
req("POST", "/api/indicator-result/dept-drill-down",
    params={"metricCode":mc,"timeDimension":"MONTH","timeValue":"2025-01"},
    desc="科室下钻计算", session=main_s, raw=True)
req("GET",  f"/api/indicator-result/dept-drill/{mc}",
    params={"timeDimension":"MONTH","timeValue":"2025-01"},
    desc="科室下钻结果", session=main_s)

# ── 数据质检 ──────────────────────────────────────────────────
log("\n" + "="*60)
log("STEP 7: 数据质检")
log("="*60)
req("POST", "/api/data-validation/check",
    params={"timeDimension":"MONTH","timeValue":"2025-01"},
    desc="数据质检", session=main_s, raw=True)
req("GET",  "/api/data-validation/history",
    params={"page":1,"size":10}, desc="质检历史", session=main_s)

# ── 指标可见范围 ──────────────────────────────────────────────
log("\n" + "="*60)
log("STEP 8: 指标可见范围")
log("="*60)
req("GET",  "/api/indicator-scope/by-dept/1",      desc="按科室查", session=main_s, raw=True)
req("GET",  f"/api/indicator-scope/by-metric/{mc}", desc="按指标查", session=main_s)

# ── 数据填报 ──────────────────────────────────────────────────
log("\n" + "="*60)
log("STEP 9: 数据填报")
log("="*60)
req("GET",  "/api/data-entry/list",  desc="填报列表", session=main_s)
req("GET",  "/api/data-entry/page",
    params={"page":1,"size":10},     desc="填报分页", session=main_s)

# ── 数据集 ────────────────────────────────────────────────────
log("\n" + "="*60)
log("STEP 10: 数据集")
log("="*60)
req("GET",  "/api/dataset/list",  desc="数据集列表", session=main_s)
req("GET",  "/api/dataset/page",
    params={"page":1,"size":10},  desc="数据集分页", session=main_s)

# ── 报告 ──────────────────────────────────────────────────────
log("\n" + "="*60)
log("STEP 11: 报告")
log("="*60)
req("GET",  "/api/report/list",  desc="报告列表", session=main_s)
req("GET",  "/api/report/page",
    params={"page":1,"size":10}, desc="报告分页", session=main_s)

# ── dataScope 权限隔离验证 ────────────────────────────────────
log("\n" + "="*60)
log("STEP 12: 角色权限隔离验证")
log("="*60)
for role, s in SESSIONS.items():
    log(f"\n  -- {role} --")
    req("GET", "/api/indicator/tree",   desc=f"{role}-指标树",   session=s)
    req("GET", "/api/indicator-scope/by-dept/1",
        desc=f"{role}-scope查询", session=s)

# ── 401 格式验证 ──────────────────────────────────────────────
log("\n" + "="*60)
log("STEP 13: 无 token 访问（验证 401 是否为 JSON）")
log("="*60)
bare = requests.Session()
req("GET", "/api/indicator/tree", desc="无token访问", session=bare, raw=True)

# ── 汇总 ──────────────────────────────────────────────────────
log("\n" + "="*60)
log("STEP 14: 汇总")
log("="*60)
# 去掉内部探测用的重复条目
real = [r for r in RESULTS if not r["desc"].startswith("_")]
ok_l   = [r for r in real if r["ok"]]
fail_l = [r for r in real if not r["ok"]]

log(f"\n  总计: {len(real)} | 正常: {len(ok_l)} | 异常: {len(fail_l)}")

if fail_l:
    log("\n  【异常接口清单（需反馈后端）】")
    for r in fail_l:
        log(f"    [{r['method']:6}] {r['path']}")
        log(f"             HTTP={r['status']} code={r['code']} msg={r['msg'][:120]}")

log("\n  【正常接口清单】")
for r in ok_l:
    log(f"    [{r['method']:6}] {r['path']}  ({r['desc']})")
