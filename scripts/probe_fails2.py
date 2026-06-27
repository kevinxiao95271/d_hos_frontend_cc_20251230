"""
probe_fails2: 跳过超时的 batchCalculate月度，继续剩余探测
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
    try: b = r.json()
    except Exception: b = {"_raw": r.text[:400]}
    return r.status_code, b

# ─────────────────────────────────────────────────────────────────
print("\n=== 1. indicator-item/save: 补 status 和 itemType ===")
combos = [
    {"itemCode": "e2e001", "itemName": "E2E", "sourceType": "AUTO", "status": "0"},
    {"itemCode": "e2e001", "itemName": "E2E", "sourceType": "AUTO", "status": "0", "itemType": "COUNT"},
    {"itemCode": "e2e001", "itemName": "E2E", "sourceType": "AUTO", "status": "0", "itemType": "RATIO"},
    {"itemCode": "a0999", "itemName": "E2E", "sourceType": "AUTO", "status": "0", "itemType": "COUNT"},
]
created_item_id = None
for p in combos:
    http, body = req("post", "/api/indicator-item/save", json=p)
    code = body.get("code"); msg = body.get("message","")[:80]
    print(f"  keys={list(p.keys())} => code={code} msg={msg}")
    if code == 200:
        created_item_id = body.get("data")
        print(f"    => ✅ 创建成功 id={created_item_id}")
        break

if created_item_id:
    req("post", "/api/indicator-item/batch", json={"ids": [created_item_id]})
    print(f"    => 已清理 id={created_item_id}")

# ─────────────────────────────────────────────────────────────────
print("\n=== 2. indicator/save: 补 status + calculateType + isLeaf ===")
combos2 = [
    {"metricCode": "e2e001", "metricName": "E2E", "metricType": "LEAF", "status": "0"},
    {"metricCode": "e2e001", "metricName": "E2E", "metricType": "LEAF",
     "status": "0", "calculateType": "FORMULA"},
    {"metricCode": "e2e001", "metricName": "E2E", "metricType": "LEAF",
     "status": "0", "calculateType": "FORMULA", "isLeaf": 1},
    {"metricCode": "e2e001", "metricName": "E2E", "metricType": "LEAF",
     "status": "0", "calculateType": "FORMULA", "isLeaf": 1, "parentCode": "GRP_SURGERY"},
]
created_metric_id = None
for p in combos2:
    http, body = req("post", "/api/indicator/save", json=p)
    code = body.get("code"); msg = body.get("message","")[:80]
    print(f"  keys={list(p.keys())} => code={code} msg={msg}")
    if code == 200:
        created_metric_id = body.get("data")
        print(f"    => ✅ 创建成功 id={created_metric_id}")
        break

if created_metric_id:
    req("delete", f"/api/indicator/{created_metric_id}")
    print(f"    => 已清理 id={created_metric_id}")

# ─────────────────────────────────────────────────────────────────
print("\n=== 3. report/task createTask: scopes 字段探测 ===")
depts = req("get", "/system/depts")[1].get("data") or []
metrics_r = req("get", "/api/indicator/page", params={"pageNum": 1, "pageSize": 3})
records = (metrics_r[1].get("data") or {}).get("records") or []
real_metric = records[0].get("metricCode", "rate_surgery_complication") if records else "rate_surgery_complication"
real_dept = depts[0] if depts else {}
dept_id = real_dept.get("deptId")
dept_code = real_dept.get("deptCode")
print(f"  真实 metricCode={real_metric!r}  deptId={dept_id}  deptCode={dept_code!r}")

task_payloads = [
    # 只带 timeDimension，不带 scopes
    {"taskName": "E2E", "timeDimension": "MONTH",
     "startDate": "2025-06-01", "endDate": "2025-06-30"},
    # 带 scopes.deptId + metricCodes
    {"taskName": "E2E", "timeDimension": "MONTH",
     "startDate": "2025-06-01", "endDate": "2025-06-30",
     "scopes": [{"deptId": dept_id, "metricCodes": [real_metric]}]},
    # 带 scopes.deptCode + metricCodes
    {"taskName": "E2E", "timeDimension": "MONTH",
     "startDate": "2025-06-01", "endDate": "2025-06-30",
     "scopes": [{"deptCode": dept_code, "metricCodes": [real_metric]}]},
    # 空 scopes
    {"taskName": "E2E", "timeDimension": "MONTH",
     "startDate": "2025-06-01", "endDate": "2025-06-30",
     "scopes": []},
    # deptIds 列表
    {"taskName": "E2E", "timeDimension": "MONTH",
     "startDate": "2025-06-01", "endDate": "2025-06-30",
     "deptIds": [dept_id], "metricCodes": [real_metric]},
]
created_task_id = None
for p in task_payloads:
    http, body = req("post", "/api/report/task", json=p)
    code = body.get("code"); msg = body.get("message","")[:80]
    scope_desc = str(p.get("scopes") or p.get("deptIds") or "无")[:60]
    print(f"  scopes={scope_desc} => code={code} msg={msg}")
    if code == 200:
        d = body.get("data") or {}
        created_task_id = d.get("taskId") if isinstance(d, dict) else d
        print(f"    => ✅ 创建成功 taskId={created_task_id}")
        break

# ─────────────────────────────────────────────────────────────────
print("\n=== 4. 系统配置权限（neuro_nurse 改配置应被拒）===")
nurse_tok = login("neuro_nurse", "Nurse@123")
r_n = requests.post(f"{BASE}/api/system/config",
    json={"hospital_name": "护士改的"},
    headers={"Authorization": f"Bearer {nurse_tok}"}, timeout=15)
try: bn = r_n.json()
except Exception: bn = {"_raw": r_n.text[:200]}
print(f"  nurse batchUpdate: HTTP={r_n.status_code} code={bn.get('code')} msg={bn.get('message','')[:80]}")
print(f"  结论: {'❌ 后端无权限控制，任何用户都可修改系统配置' if bn.get('code') == 200 else '✅ 正确被拒绝'}")

# ─────────────────────────────────────────────────────────────────
print("\n=== 5. 查 neuro_nurse my-tasks 的状态 (304091 原因) ===")
nurse_tok2 = login("neuro_nurse", "Nurse@123")
Hn = {"Authorization": f"Bearer {nurse_tok2}"}
mt = requests.get(f"{BASE}/api/report/task/my-tasks", headers=Hn, timeout=15).json()
my = mt.get("data") or []
print(f"  my-tasks count={len(my)}")
for t in my:
    print(f"    taskId={t.get('taskId')} status={t.get('status')} fillStatus={t.get('fillStatus')} taskName={t.get('taskName','')}")

# 找一个 PUBLISHED/OPEN 状态的任务，尝试 saveItem
target_task = next((t for t in my if t.get("status") in ("PUBLISHED", "OPEN", "PENDING")), None)
if target_task:
    tid = target_task.get("taskId")
    # 拿 sheet
    sheet_r = requests.get(f"{BASE}/api/report/data/sheet",
        params={"taskId": tid}, headers=Hn, timeout=15).json()
    sheet = sheet_r.get("data") or []
    print(f"  使用 taskId={tid} status={target_task.get('status')} sheet items={len(sheet)}")
    if sheet:
        row = sheet[0]
        mc = row.get("metricCode") or real_metric
        save_body = {"taskId": tid, "metricCode": mc, "value": "99", "remark": "probe"}
        sr = requests.post(f"{BASE}/api/report/data/save", json=save_body, headers=Hn, timeout=15)
        sb = sr.json()
        print(f"  saveItem: HTTP={sr.status_code} code={sb.get('code')} msg={sb.get('message','')[:80]}")
else:
    print("  没有找到 PUBLISHED/OPEN 状态的任务，全部已提交/关闭")

# ─────────────────────────────────────────────────────────────────
print("\n=== 6. validateSql 危险 SQL 应被拒绝（安全漏洞验证）===")
dangerous = [
    "DROP TABLE patient",
    "DELETE FROM patient",
    "UPDATE patient SET status=0",
    "SELECT * FROM patient; DROP TABLE patient--",
]
for sql in dangerous:
    http, body = req("post", "/api/indicator-item/validate-sql", json={"sql": sql})
    code = body.get("code"); msg = body.get("message","")[:60]
    print(f"  sql={sql[:40]!r} => code={code} {'❌ 未被拒绝' if code == 200 else '✅ 已拒绝'} msg={msg}")

print()
