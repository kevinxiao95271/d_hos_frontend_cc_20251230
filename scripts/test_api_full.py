# -*- coding: utf-8 -*-
"""
后端 API 全面测试脚本 - 暴露所有问题，不兜底
BASE: http://81.71.44.180:8070/dgear
登录: POST /auth/login?username=xxx&password=xxx  (query params, not body)
"""
import sys
import requests
import json

# Windows terminal encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://81.71.44.180:8070/dgear"
session = requests.Session()
session.headers.update({"Content-Type": "application/json"})

RESULTS = []

def log(s):
    print(s, flush=True)

def req(method, path, params=None, data=None, desc="", raw=False):
    url = BASE + path
    try:
        r = session.request(method, url, params=params, json=data, timeout=15)
        status = r.status_code
        try:
            body = r.json()
            code = body.get("code", "-") if isinstance(body, dict) else "-"
            msg  = (body.get("message") or body.get("msg") or "") if isinstance(body, dict) else ""
        except:
            body = r.text[:200]
            code = "-"
            msg  = str(body)

        ok = status == 200 and str(code) in ("200", "0", "00000", "success", "true", "1")
        flag = "OK" if ok else "FAIL"
        log(f"  [{flag}] {method:6} {path}")
        log(f"         HTTP={status} code={code} msg={msg[:120]}")
        if raw:
            log(f"         RAW={json.dumps(body, ensure_ascii=False)[:400]}")
        RESULTS.append({"method": method, "path": path, "status": status,
                        "code": code, "msg": msg, "desc": desc, "ok": ok})
        return r, body
    except Exception as e:
        log(f"  [ERR]  {method:6} {path}")
        log(f"         ERROR={e}")
        RESULTS.append({"method": method, "path": path, "status": "ERR",
                        "code": "-", "msg": str(e), "desc": desc, "ok": False})
        return None, None


# ============================================================
log("="*60)
log("STEP 1: Swagger 文档探测")
log("="*60)
for swagger_path in [
    "/v3/api-docs",
    "/swagger-ui/index.html",
    "/v2/api-docs",
    "/swagger-ui.html",
    "/doc.html",
]:
    try:
        r = requests.get(BASE + swagger_path, timeout=8)
        log(f"  {swagger_path}  ->  HTTP {r.status_code}")
    except Exception as e:
        log(f"  {swagger_path}  ->  ERROR: {e}")


# ============================================================
log("\n" + "="*60)
log("STEP 2: 登录测试（注意: 参数以 query params 发送）")
log("="*60)
TOKEN = None
accounts = [
    ("admin",   "admin123"),
    ("admin",   "Admin@123"),
    ("admin",   "123456"),
    ("admin",   "admin"),
    ("test",    "test123"),
]
for user, pwd in accounts:
    r, body = req("POST", "/auth/login",
                  params={"username": user, "password": pwd},
                  desc="登录", raw=True)
    if r and r.status_code == 200 and isinstance(body, dict):
        token = None
        if body.get("code") == 200:
            d = body.get("data") or {}
            token = d.get("token") if isinstance(d, dict) else None
        elif "token" in body:
            token = body["token"]
        if token:
            TOKEN = token
            log(f"  >>> 登录成功! token={TOKEN[:50]}...")
            session.headers["Authorization"] = f"Bearer {TOKEN}"
            break


# ============================================================
log("\n" + "="*60)
log("STEP 3: 无需登录的接口")
log("="*60)
req("GET", "/auth/login", desc="GET 登录页（应返回405或404）")


# ============================================================
log("\n" + "="*60)
log("STEP 4: 需要 token 的接口测试")
log("="*60)

# -- 用户 & 角色 --
log("\n-- 用户/认证模块 --")
req("GET",  "/auth/userInfo",            desc="获取当前用户信息")
req("GET",  "/auth/menus",               desc="获取菜单列表", params={"roleId": 1})
req("GET",  "/system/users",             desc="用户列表")
req("GET",  "/system/roles",             desc="角色列表")
req("GET",  "/system/depts",             desc="科室列表")

# -- 指标项 --
log("\n-- 指标项模块 --")
req("GET",  "/api/indicator-item/list",  desc="指标项列表")
req("GET",  "/api/indicator-item/page",  desc="指标项分页", params={"page":1,"size":10})
req("GET",  "/api/indicator-item/1",     desc="指标项详情 id=1")
req("POST", "/api/indicator-item/1/execute",
    params={"timeDimension":"MONTH","timeValue":"2024-01"},
    desc="执行指标项")

# -- 指标 --
log("\n-- 指标模块 --")
req("GET",  "/api/indicator/tree",       desc="指标树")
req("GET",  "/api/indicator/page",       desc="指标分页", params={"page":1,"size":10})
req("GET",  "/api/indicator/1",          desc="指标详情 id=1")

# -- 指标计算结果 --
log("\n-- 指标计算结果模块 --")
req("POST", "/api/indicator-result/calculate",
    params={"metricCode":"TEST","timeDimension":"MONTH","timeValue":"2024-01"},
    desc="单指标计算")
req("GET",  "/api/indicator-result/list",
    params={"metricCode":"TEST","timeDimension":"MONTH","timeValue":"2024-01"},
    desc="指标结果列表")
req("POST", "/api/indicator-result/dept-drill-down",
    params={"metricCode":"TEST","timeDimension":"MONTH","timeValue":"2024-01"},
    desc="科室下钻计算")
req("GET",  "/api/indicator-result/dept-drill/TEST",
    params={"timeDimension":"MONTH","timeValue":"2024-01"},
    desc="科室下钻结果")

# -- 数据质检 --
log("\n-- 数据质检模块 --")
req("POST", "/api/data-validation/check",
    params={"timeDimension":"MONTH","timeValue":"2024-01"},
    desc="数据质检")
req("GET",  "/api/data-validation/history",
    params={"page":1,"size":10},
    desc="质检历史")

# -- 指标可见范围 --
log("\n-- 指标可见范围模块 --")
req("GET",  "/api/indicator-scope/by-dept/1",    desc="按科室查可见范围")
req("GET",  "/api/indicator-scope/by-metric/TEST", desc="按指标查可见范围")
req("POST", "/api/indicator-scope/binding",
    data={"deptId":1,"metricCode":"TEST"},
    desc="添加绑定")

# -- 数据填报 --
log("\n-- 数据填报模块 --")
req("GET",  "/api/data-entry/list",        desc="填报列表")
req("GET",  "/api/data-entry/page",        desc="填报分页", params={"page":1,"size":10})

# -- 数据集 --
log("\n-- 数据集模块 --")
req("GET",  "/api/dataset/list",           desc="数据集列表")
req("GET",  "/api/dataset/page",           desc="数据集分页", params={"page":1,"size":10})

# -- 报告 --
log("\n-- 报告模块 --")
req("GET",  "/api/report/list",            desc="报告列表")
req("GET",  "/api/report/page",            desc="报告分页", params={"page":1,"size":10})


# ============================================================
log("\n" + "="*60)
log("STEP 5: 汇总报告")
log("="*60)
ok_list   = [r for r in RESULTS if r["ok"]]
fail_list = [r for r in RESULTS if not r["ok"]]

log(f"\n  总计: {len(RESULTS)} | 正常: {len(ok_list)} | 异常: {len(fail_list)}")

if fail_list:
    log("\n  【异常接口清单】")
    for r in fail_list:
        log(f"    [{r['method']:6}] {r['path']}")
        log(f"             HTTP={r['status']} code={r['code']}")
        log(f"             msg ={r['msg'][:150]}")
        log(f"             desc={r['desc']}")

log("\n  【正常接口清单】")
for r in ok_list:
    log(f"    [{r['method']:6}] {r['path']}  ({r['desc']})")
