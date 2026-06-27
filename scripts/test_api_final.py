# -*- coding: utf-8 -*-
"""最终验证：计算接口用正确参数（startDate+endDate）"""
import sys, requests, json
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://localhost:8070/dgear"

def log(s): print(s, flush=True)

# 登录
s = requests.Session()
r = s.post(BASE + "/auth/login",
           data={"username":"admin","password":"Admin@123"},
           headers={"Content-Type":"application/x-www-form-urlencoded"}, timeout=10)
body = r.json()
if body.get("code") == 200:
    s.headers["Authorization"] = f"Bearer {body['data']['token']}"
    log(f"登录成功")
else:
    log(f"登录失败: {body}")
    sys.exit(1)

def req(method, path, params=None, desc=""):
    r = s.request(method, BASE+path, params=params, timeout=20)
    body = r.json()
    code = body.get("code")
    msg  = body.get("message","")
    data = body.get("data")
    flag = "OK  " if code == 200 else "FAIL"
    log(f"  [{flag}] {desc}")
    log(f"          {method} {path}")
    log(f"          code={code} msg={msg}")
    if code == 200 and data is not None:
        log(f"          data={json.dumps(data, ensure_ascii=False)[:300]}")
    return code, data

log("\n=== 计算接口：月度（2025-01）===")
req("POST", "/api/indicator-result/calculate", params={
    "metricCode":"rate_incision_infection",
    "timeDimension":"MONTH",
    "startDate":"2025-01-01",
    "endDate":"2025-01-31"
}, desc="calculate MONTH 2025-01")

log("\n=== 计算接口：年度（2020，有数据）===")
req("POST", "/api/indicator-result/calculate", params={
    "metricCode":"rate_surgery_complication",
    "timeDimension":"YEAR",
    "startDate":"2020-01-01",
    "endDate":"2020-12-31"
}, desc="calculate YEAR 2020")

log("\n=== 指标项执行：月度 ===")
req("POST", "/api/indicator-item/a0050/execute", params={
    "startDate":"2025-01-01",
    "endDate":"2025-01-31"
}, desc="execute a0050 MONTH 2025-01")

log("\n=== 科室下钻：年度 ===")
req("POST", "/api/indicator-result/dept-drill-down", params={
    "metricCode":"rate_surgery_complication",
    "timeDimension":"YEAR",
    "startDate":"2020-01-01",
    "endDate":"2020-12-31"
}, desc="dept-drill-down YEAR 2020")

log("\n=== 父节点应返回 30400 ===")
req("POST", "/api/indicator-result/calculate", params={
    "metricCode":"GRP_SURGERY",
    "timeDimension":"YEAR",
    "startDate":"2020-01-01",
    "endDate":"2020-12-31"
}, desc="父节点-期望30400")
