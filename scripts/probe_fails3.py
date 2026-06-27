"""probe_fails3: 继续 indicator/save 和 createTask 最后探测"""
import sys, requests
sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://localhost:8070/dgear"
tok = requests.post(f"{BASE}/auth/login",
    data={"username":"admin","password":"Admin@123"},
    headers={"Content-Type":"application/x-www-form-urlencoded"}, timeout=15
).json()["data"]["token"]
H = {"Authorization": f"Bearer {tok}"}

def req(method, path, **kw):
    r = getattr(requests, method)(f"{BASE}{path}", headers=H, timeout=30, **kw)
    try: b = r.json()
    except Exception: b = {"_raw": r.text[:400]}
    return r.status_code, b

# ─── indicator/save ─────────────────────────────────────────────
print("=== indicator/save: isLeaf=1 + calculateType 矛盾探测 ===")
cases = [
    # calculateType 各种枚举
    {"metricCode":"e2e001","metricName":"E2E","metricType":"LEAF","status":"0","isLeaf":1,"calculateType":"FORMULA"},
    {"metricCode":"e2e001","metricName":"E2E","metricType":"LEAF","status":"0","isLeaf":1,"calculateType":"SQL"},
    {"metricCode":"e2e001","metricName":"E2E","metricType":"LEAF","status":"0","isLeaf":1,"calculateType":"MANUAL"},
    {"metricCode":"e2e001","metricName":"E2E","metricType":"LEAF","status":"0","isLeaf":1,"calculateType":"AUTO"},
    # 用 0/1
    {"metricCode":"e2e001","metricName":"E2E","metricType":"LEAF","status":"0","isLeaf":1,"calcType":"FORMULA"},
    # metricType=LEAF 可能对应的正确 calculateType
    {"metricCode":"e2e001","metricName":"E2E","metricType":"LEAF","status":0,"isLeaf":1,"calculateType":"FORMULA"},
    # status=0(int) vs "0"(str)
    {"metricCode":"e2e001","metricName":"E2E","status":0,"isLeaf":1,"calculateType":"FORMULA"},
]
for p in cases:
    http, body = req("post", "/api/indicator/save", json=p)
    code = body.get("code"); msg = body.get("message","")[:80]
    print(f"  {p}")
    print(f"    => code={code} msg={msg}")
    if code == 200:
        mid = body.get("data")
        print(f"    ✅ 成功! id={mid}")
        req("delete", f"/api/indicator/{mid}")
        break

# ─── createTask: 字段名探测 ─────────────────────────────────────
print("\n=== createTask: taskName 字段名探测 (deptId 方式) ===")
# 拿真实 deptId, metricCode
depts = req("get", "/system/depts")[1].get("data") or []
dept_id = depts[0].get("deptId") if depts else 1
metrics = (req("get","/api/indicator/page",params={"pageNum":1,"pageSize":3})[1].get("data") or {}).get("records") or []
mc = metrics[0].get("metricCode","rate_surgery_complication") if metrics else "rate_surgery_complication"

task_cases = [
    # 只有 deptId scope 不带 name
    {"name":"E2E任务","timeDimension":"MONTH","startDate":"2025-06-01","endDate":"2025-06-30",
     "scopes":[{"deptId": dept_id,"metricCodes":[mc]}]},
    # task_name
    {"task_name":"E2E任务","timeDimension":"MONTH","startDate":"2025-06-01","endDate":"2025-06-30",
     "scopes":[{"deptId": dept_id,"metricCodes":[mc]}]},
    # 完整标准 taskName
    {"taskName":"E2E任务","timeDimension":"MONTH","startDate":"2025-06-01","endDate":"2025-06-30",
     "scopes":[{"deptId": dept_id,"metricCodes":[mc]}]},
    # startPeriod/endPeriod 方式
    {"taskName":"E2E任务","timeDimension":"MONTH","startPeriod":"202506","endPeriod":"202506",
     "scopes":[{"deptId": dept_id,"metricCodes":[mc]}]},
    # 不带 scopes，带 deptIds
    {"taskName":"E2E任务","timeDimension":"MONTH","startDate":"2025-06-01","endDate":"2025-06-30",
     "deptIds":[dept_id],"metricCodes":[mc]},
]
created_task = None
for p in task_cases:
    http, body = req("post", "/api/report/task", json=p)
    code = body.get("code"); msg = body.get("message","")[:80]
    print(f"  payload_keys={list(p.keys())} scopes_keys={list((p.get('scopes') or [{}])[0].keys())}")
    print(f"    => code={code} msg={msg}")
    if code == 200:
        d = body.get("data") or {}
        tid = d.get("taskId") if isinstance(d,dict) else d
        print(f"    ✅ 成功! taskId={tid}")
        created_task = tid
        break

# 如果 createTask 成功，尝试完整流程
if created_task:
    print(f"\n=== createTask 成功后，尝试 publish + sheet + saveItem ===")
    http, body = req("post", f"/api/report/task/{created_task}/publish")
    print(f"  publish: code={body.get('code')} msg={body.get('message','')[:60]}")
    # neuro_nurse 侧
    nurse_tok = requests.post(f"{BASE}/auth/login",
        data={"username":"neuro_nurse","password":"Nurse@123"},
        headers={"Content-Type":"application/x-www-form-urlencoded"}, timeout=15
    ).json()["data"]["token"]
    Hn = {"Authorization": f"Bearer {nurse_tok}"}
    mt = requests.get(f"{BASE}/api/report/task/my-tasks", headers=Hn, timeout=15).json()
    print(f"  neuro_nurse my-tasks 更新后 count={len(mt.get('data') or [])}")
    # 获取 sheet
    sheet_r = requests.get(f"{BASE}/api/report/data/sheet",
        params={"taskId": created_task}, headers=Hn, timeout=15).json()
    sheet = sheet_r.get("data") or []
    print(f"  sheet items={len(sheet)}")
    if sheet:
        row = sheet[0]
        sr = requests.post(f"{BASE}/api/report/data/save",
            json={"taskId": created_task, "metricCode": row.get("metricCode",mc),
                  "value": "88", "remark": "e2e_probe"},
            headers=Hn, timeout=15).json()
        print(f"  saveItem: code={sr.get('code')} msg={sr.get('message','')[:60]}")

print()
