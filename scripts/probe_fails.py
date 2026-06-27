"""
针对 e2e_test 失败项的深度探测
"""
import sys, json, requests
sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://localhost:8070/dgear"

def login(u, p):
    r = requests.post(f"{BASE}/auth/login",
        data={"username": u, "password": p},
        headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=15)
    return r.json()["data"]["token"]

tok = login("admin", "Admin@123")
H = {"Authorization": f"Bearer {tok}"}

def req(method, path, **kw):
    r = getattr(requests, method)(f"{BASE}{path}", headers=H, timeout=30, **kw)
    try:
        b = r.json()
    except Exception:
        b = {"_raw": r.text[:400]}
    return r.status_code, b

def show(label, http, body):
    code = body.get("code") if isinstance(body, dict) else "?"
    msg  = body.get("message", "") if isinstance(body, dict) else str(body)[:100]
    print(f"  {label}: HTTP={http} code={code} msg={msg[:100]}")


# ─────────────────────────────────────────────────────────────────
print("\n=== 1. indicator-item/save: itemCode 格式规则探测 ===")
for item_code in ["test001", "a0999", "a_999", "e2e001", "E2ETEST", "z9999"]:
    http, body = req("post", "/api/indicator-item/save",
        json={"itemCode": item_code, "itemName": f"测试{item_code}", "sourceType": "AUTO"})
    show(item_code, http, body)
    # 如果成功了清理掉
    if body.get("code") == 200 and isinstance(body.get("data"), int):
        req("post", "/api/indicator-item/batch", json={"ids": [body["data"]]})

# ─────────────────────────────────────────────────────────────────
print("\n=== 2. indicator/save: 缺少哪个必填参数 ===")
payloads = [
    {"metricCode": "e2e001", "metricName": "E2E"},
    {"metricCode": "e2e001", "metricName": "E2E", "metricType": "LEAF"},
    {"metricCode": "e2e001", "metricName": "E2E", "metricType": "GROUP"},
    {"metricCode": "e2e001", "metricName": "E2E", "metricType": "LEAF", "parentCode": "GRP_SURGERY"},
    {"metricCode": "e2e001", "metricName": "E2E", "metricType": "LEAF", "parentCode": "GRP_SURGERY", "unit": "%"},
]
for p in payloads:
    http, body = req("post", "/api/indicator/save", json=p)
    keys = list(p.keys())
    code = body.get("code")
    msg  = body.get("message", "")[:80]
    print(f"  keys={keys}")
    print(f"    => code={code} msg={msg}")
    if code == 200 and isinstance(body.get("data"), int):
        req("delete", f"/api/indicator/{body['data']}")
        break

# ─────────────────────────────────────────────────────────────────
print("\n=== 3. scope addBinding: 用真实 deptCode ===")
depts_resp = req("get", "/system/depts")
depts = depts_resp[1].get("data") or []
print(f"  科室列表前3: {[d.get('deptCode') for d in depts[:3]]}")
for dept in depts[:3]:
    dc = dept.get("deptCode") or dept.get("deptId")
    http, body = req("post", "/api/indicator-scope/binding",
        json={"metricCode": "rate_surgery_complication", "deptCode": str(dc)})
    show(f"deptCode={dc}", http, body)

# ─────────────────────────────────────────────────────────────────
print("\n=== 4. batchCalculate 月度 (看完整响应) ===")
http, body = req("post", "/api/indicator-result/batch-calculate",
    params={"timeDimension": "MONTH", "startDate": "2020-01-01", "endDate": "2020-06-30"})
print(f"  HTTP={http} code={body.get('code')} msg={body.get('message','')[:120]}")
if "_raw" in body:
    print(f"  RAW(前200)={body['_raw'][:200]}")

# ─────────────────────────────────────────────────────────────────
print("\n=== 5. report/task createTask: Swagger 字段探测 ===")
# 先看真实存在的 metricCode
metrics_r = req("get", "/api/indicator/page", params={"pageNum": 1, "pageSize": 3})
records = (metrics_r[1].get("data") or {}).get("records") or []
real_metric = records[0].get("metricCode") if records else "rate_surgery_complication"
print(f"  使用真实 metricCode={real_metric!r}")

task_payloads = [
    {"taskName": "E2E任务", "timeDimension": "MONTH",
     "startDate": "2025-06-01", "endDate": "2025-06-30"},

    {"taskName": "E2E任务", "timeDimension": "MONTH",
     "startDate": "2025-06-01", "endDate": "2025-06-30",
     "scopes": [{"deptCode": "dept_neurology", "metricCodes": [real_metric]}]},

    {"taskName": "E2E任务", "timeDimension": "MONTH",
     "startDate": "2025-06-01", "endDate": "2025-06-30",
     "deptScopes": [{"deptCode": "dept_neurology", "metricCodes": [real_metric]}]},

    # 用真实科室 code
    *(
        [{"taskName": "E2E任务", "timeDimension": "MONTH",
          "startDate": "2025-06-01", "endDate": "2025-06-30",
          "scopes": [{"deptCode": depts[0].get("deptCode", ""), "metricCodes": [real_metric]}]}]
        if depts else []
    ),

    # scopes 用 deptId
    *(
        [{"taskName": "E2E任务", "timeDimension": "MONTH",
          "startDate": "2025-06-01", "endDate": "2025-06-30",
          "scopes": [{"deptId": depts[0].get("deptId"), "metricCodes": [real_metric]}]}]
        if depts else []
    ),
]
for p in task_payloads:
    http, body = req("post", "/api/report/task", json=p)
    code = body.get("code")
    msg  = body.get("message", "")[:80]
    scope_key = list((p.get("scopes") or p.get("deptScopes") or [{}])[0].keys()) if "scopes" in p or "deptScopes" in p else "无scopes"
    print(f"  scope_key={scope_key} => code={code} msg={msg}")
    if code == 200:
        tid = (body.get("data") or {}).get("taskId") or body.get("data")
        print(f"    ✅ 成功! taskId={tid}")
        break

# ─────────────────────────────────────────────────────────────────
print("\n=== 6. 系统配置权限：neuro_nurse 能改系统配置? ===")
nurse_tok = login("neuro_nurse", "Nurse@123")
Hn = {"Authorization": f"Bearer {nurse_tok}"}
r_nurse = requests.post(f"{BASE}/api/system/config",
    json={"hospital_name": "护士改的"},
    headers=Hn, timeout=15)
try:
    bn = r_nurse.json()
except Exception:
    bn = {"_raw": r_nurse.text[:200]}
print(f"  nurse batchUpdate: HTTP={r_nurse.status_code} code={bn.get('code')} msg={bn.get('message','')[:80]}")

print("\n=== 7. saveItem 304091 是什么状态冲突 ===")
# 用 admin 看现有任务里的状态
tasks_r = req("get", "/api/report/task/page", params={"pageNum": 1, "pageSize": 5})
tasks_data = (tasks_r[1].get("data") or {}).get("records") or []
print(f"  现有任务前3:")
for t in tasks_data[:3]:
    print(f"    taskId={t.get('taskId')} name={t.get('taskName')} status={t.get('status')}")
# 看 my-tasks 状态
nurse_tok2 = login("neuro_nurse", "Nurse@123")
Hn2 = {"Authorization": f"Bearer {nurse_tok2}"}
mt = requests.get(f"{BASE}/api/report/task/my-tasks", headers=Hn2, timeout=15).json()
my = (mt.get("data") or [])
print(f"  neuro_nurse my-tasks:")
for t in my[:3]:
    print(f"    taskId={t.get('taskId')} status={t.get('status')} fillStatus={t.get('fillStatus')}")

print()
