"""验证后端 B1-B6 六个修复是否真的生效"""
import sys, requests
sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://localhost:8070/dgear"

def login(u, p):
    r = requests.post(f"{BASE}/auth/login",
        data={"username": u, "password": p},
        headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=30)
    return r.json()["data"]["token"]

tok   = login("admin",       "Admin@123")
n_tok = login("neuro_nurse", "Nurse@123")
H  = {"Authorization": f"Bearer {tok}"}
Hn = {"Authorization": f"Bearer {n_tok}"}

results = []

def chk(label, ok, detail=""):
    mark = "PASS" if ok else "FAIL"
    results.append((mark, label, detail))
    icon = "✅" if ok else "❌"
    print(f"  [{icon}] {label}")
    print(f"       {detail}")

# ──────────────────────────────────────────────────────────────
print("\n=== B1: validateSql 危险 SQL 应返回 30400 ===")
dangerous_sqls = [
    "DROP TABLE patient",
    "DELETE FROM patient",
    "UPDATE patient SET status=0",
    "SELECT * FROM patient; DROP TABLE patient--",
]
for sql in dangerous_sqls:
    r = requests.post(f"{BASE}/api/indicator-item/validate-sql",
        json={"sql": sql}, headers=H, timeout=10).json()
    code = r.get("code")
    chk(f"B1 validateSql({sql[:30]!r})", code != 200,
        f"code={code}  msg={r.get('message','')[:60]}")

# ──────────────────────────────────────────────────────────────
print("\n=== B2: validateExpression 非法表达式应返回 30400 ===")
invalid_exprs = ["!@#非法%%%", "((( broken", ";;;invalid;;;"]
for expr in invalid_exprs:
    r = requests.post(f"{BASE}/api/indicator/validate-expression",
        json={"expression": expr}, headers=H, timeout=10).json()
    code = r.get("code")
    chk(f"B2 validateExpression({expr!r})", code != 200,
        f"code={code}  msg={r.get('message','')[:60]}")

# ──────────────────────────────────────────────────────────────
print("\n=== B3: indicator/save 叶子节点(isLeaf=1)应成功 ===")
payload = {
    "metricCode": "e2e_b3_verify",
    "metricName": "B3验证叶子节点",
    "isLeaf": 1,
    "metricType": "QUANTITATIVE",
    "calculationType": "EXPRESSION",
    "status": "0",
}
r = requests.post(f"{BASE}/api/indicator/save", json=payload, headers=H, timeout=10).json()
code = r.get("code")
ok = code == 200
chk("B3 save(isLeaf=1, calculationType=EXPRESSION)", ok,
    f"code={code}  msg={r.get('message','')[:70]}")
# 清理
if ok:
    d = r.get("data")
    mid = d.get("id") if isinstance(d, dict) else (d if isinstance(d, int) else None)
    if mid:
        requests.delete(f"{BASE}/api/indicator/{mid}", headers=H, timeout=10)

# ──────────────────────────────────────────────────────────────
print("\n=== B4: scope addBinding 传 deptId 整数主键 ===")
depts = requests.get(f"{BASE}/system/depts", headers=H, timeout=10).json().get("data") or []
dept0 = depts[0] if depts else {"deptId": 1, "deptCode": "1001"}
dept_id   = dept0.get("deptId")
dept_code = dept0.get("deptCode")

# 传 deptId → 应 200
r = requests.post(f"{BASE}/api/indicator-scope/binding",
    json={"deptId": dept_id, "metricCode": "rate_surgery_complication", "isPrimaryOwner": 1},
    headers=H, timeout=10).json()
chk(f"B4 addBinding(deptId={dept_id}) 应 200",
    r.get("code") == 200,
    f"code={r.get('code')}  msg={r.get('message','')[:60]}")

# 传 deptCode 字符串（无 deptId）→ 应 30400
r2 = requests.post(f"{BASE}/api/indicator-scope/binding",
    json={"deptCode": dept_code, "metricCode": "rate_surgery_complication"},
    headers=H, timeout=10).json()
chk(f"B4 addBinding(deptCode={dept_code!r}, 无 deptId) 应 30400",
    r2.get("code") == 30400,
    f"code={r2.get('code')}  msg={r2.get('message','')[:60]}")

# ──────────────────────────────────────────────────────────────
print("\n=== B5: batchCalculate 月度 <=3 期 / >3 期 ===")
# 6 个月 → 应 30400
r = requests.post(f"{BASE}/api/indicator-result/batch-calculate",
    params={"timeDimension": "MONTH", "startDate": "2020-01-01", "endDate": "2020-06-30"},
    headers=H, timeout=15).json()
chk("B5 batchCalculate(6 个月) 应 30400",
    r.get("code") == 30400,
    f"code={r.get('code')}  msg={r.get('message','')[:70]}")

# 3 个月 → 应 200（允许最多 60s）
r2 = requests.post(f"{BASE}/api/indicator-result/batch-calculate",
    params={"timeDimension": "MONTH", "startDate": "2020-01-01", "endDate": "2020-03-31"},
    headers=H, timeout=120).json()
chk("B5 batchCalculate(3 个月) 应 200",
    r2.get("code") == 200,
    f"code={r2.get('code')}  msg={r2.get('message','')[:60]}")

# ──────────────────────────────────────────────────────────────
print("\n=== B6: systemConfig 权限鉴别 ===")
# neuro_nurse 写 → 应 30403
rn = requests.post(f"{BASE}/api/system/config",
    json={"hospital_name": "护士改的"}, headers=Hn, timeout=10).json()
chk("B6 systemConfig(neuro_nurse) 应 30403",
    rn.get("code") == 30403,
    f"code={rn.get('code')}  msg={rn.get('message','')[:60]}")

# admin 写 → 应 200
ra = requests.post(f"{BASE}/api/system/config",
    json={"hospital_name": "端到端验证医院"}, headers=H, timeout=10).json()
chk("B6 systemConfig(admin) 应 200",
    ra.get("code") == 200,
    f"code={ra.get('code')}  msg={ra.get('message','')[:50]}")

# ──────────────────────────────────────────────────────────────
PASS = sum(1 for r in results if r[0] == "PASS")
FAIL = sum(1 for r in results if r[0] == "FAIL")
print(f"\n{'='*60}")
print(f"  验证汇总  共 {len(results)} 项   ✅ PASS={PASS}   ❌ FAIL={FAIL}")
print(f"{'='*60}")
if FAIL:
    print("\n❌ 未通过项：")
    for r in results:
        if r[0] == "FAIL":
            print(f"  {r[1]}")
            print(f"    {r[2]}")
print()
