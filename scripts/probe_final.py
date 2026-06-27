"""probe_final: 验证 calculationType vs calculateType，以及 status:1 vs 0"""
import sys, requests
sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://localhost:8070/dgear"
tok = requests.post(f"{BASE}/auth/login",
    data={"username":"admin","password":"Admin@123"},
    headers={"Content-Type":"application/x-www-form-urlencoded"}, timeout=15
).json()["data"]["token"]
H = {"Authorization": f"Bearer {tok}"}

def req(method, path, **kw):
    r = getattr(requests, method)(f"{BASE}{path}", headers=H, timeout=20, **kw)
    try: b = r.json()
    except Exception: b = {"_raw": r.text[:300]}
    return r.status_code, b

# ── 1. indicator/save: calculationType vs calculateType ────────
print("=== indicator/save: calculationType (带ion) ===")
cases = [
    {"metricCode":"e2e001","metricName":"E2E","isLeaf":1,"status":"0","calculationType":"FORMULA"},
    {"metricCode":"e2e001","metricName":"E2E","isLeaf":1,"status":"0","calculationType":"EXPRESSION"},
    {"metricCode":"e2e001","metricName":"E2E","isLeaf":1,"status":"0","calculationType":"NONE"},
    {"metricCode":"e2e001","metricName":"E2E","isLeaf":1,"status":"0","calculationType":"ITEM"},
    {"metricCode":"e2e001","metricName":"E2E","isLeaf":0,"status":"0"},  # 非叶子不需要 calculationType
]
for p in cases:
    http, body = req("post", "/api/indicator/save", json=p)
    code = body.get("code"); msg = body.get("message","")[:80]
    print(f"  {p} => code={code} msg={msg}")
    if code == 200:
        mid = body.get("data")
        print(f"    ✅ id={mid}")
        req("delete", f"/api/indicator/{mid}")
        break

# ── 2. indicator-item: itemType枚举探测 ────────────────────────
print("\n=== indicator-item: 现有记录 itemType 枚举值 ===")
http, body = req("get", "/api/indicator-item/list")
items = body.get("data") or []
types = set(i.get("itemType") for i in items if i.get("itemType"))
print(f"  现有 itemType 枚举值: {types}")
print(f"  现有前3条: {[{k:i[k] for k in ['itemCode','itemType','status'] if k in i} for i in items[:3]]}")

# ── 3. indicator-item: status 1(int) vs "0"(str) 的影响 ────────
print("\n=== indicator-item: status=1(disabled) 测试 ===")
http, body = req("post", "/api/indicator-item/save",
    json={"itemCode":"e2e001","itemName":"E2E","sourceType":"AUTO","status":1,"itemType":list(types)[0] if types else "COUNT"})
code = body.get("code"); msg = body.get("message","")[:80]
d = body.get("data") or {}
print(f"  status=1(int): code={code} msg={msg}")
if code == 200:
    saved_status = d.get("status") if isinstance(d,dict) else None
    print(f"  保存后 status 值: {saved_status}")
    mid = d.get("id") if isinstance(d,dict) else (d if isinstance(d,int) else None)
    if mid: req("post","/api/indicator-item/batch",json={"ids":[mid]})

# ── 4. createTask: name 字段探测，以及 data 返回结构 ──────────
print("\n=== createTask: name 字段 + 返回 taskId ===")
depts = req("get","/system/depts")[1].get("data") or []
dept_id = depts[0].get("deptId") if depts else 1
metrics = (req("get","/api/indicator/page",params={"pageNum":1,"pageSize":3})[1].get("data") or {}).get("records") or []
mc = metrics[0].get("metricCode","rate_surgery_complication") if metrics else "rate_surgery_complication"

http, body = req("post", "/api/report/task", json={
    "name": "E2E最终测试",
    "timeDimension": "MONTH",
    "startDate": "2025-06-01",
    "endDate": "2025-06-30",
    "scopes": [{"deptId": dept_id, "metricCodes": [mc]}]
})
code = body.get("code"); msg = body.get("message","")[:80]
d = body.get("data")
print(f"  createTask: code={code} msg={msg}")
print(f"  data 结构: type={type(d).__name__} value={d}")
if isinstance(d, dict):
    print(f"  data 字段: {list(d.keys())}")
    tid = d.get("taskId") or d.get("id") or d.get("task_id")
    print(f"  提取到 taskId={tid}")
elif isinstance(d, int):
    print(f"  data 是整数 id={d}")
    tid = d
else:
    tid = None

# 如果成功，清理
if code == 200 and tid:
    req("post", f"/api/report/task/{tid}/close")
    print(f"  已关闭任务 {tid}")

print()
