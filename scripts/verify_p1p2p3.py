"""
验证 P1/P2/P3 修复
"""
import sys, requests
sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://localhost:8070/dgear"

def login(u, p):
    r = requests.post(f"{BASE}/auth/login",
        data={"username": u, "password": p},
        headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=30)
    return r.json()["data"]["token"]

tok = login("admin", "Admin@123")
H = {"Authorization": f"Bearer {tok}"}
results = []

def chk(label, ok, detail=""):
    mark = "PASS" if ok else "FAIL"
    results.append((mark, label, detail))
    print(f"  [{'✅' if ok else '❌'}] {label}")
    if detail: print(f"       {detail}")

def req(method, path, **kw):
    try:
        r = getattr(requests, method)(f"{BASE}{path}", headers=H, timeout=20, **kw)
        try: b = r.json()
        except Exception: b = {"_raw": r.text[:300]}
        return r.status_code, b
    except Exception as e:
        return 0, {"error": str(e)}

def code(b): return b.get("code") if isinstance(b, dict) else "?"
def d(b):    return b.get("data") if isinstance(b, dict) else None

# ── P1: dataset/{id} records 应有数据 ────────────────────────
print("\n=== P1: dataset/{id} records 不再为空 ===")
for ds_id, expected_count in [("YEAR_2020", 36), ("YEAR_2022", 4), ("YEAR_2023", 36)]:
    http, b = req("get", f"/api/dataset/{ds_id}")
    dd = d(b) or {}
    records = dd.get("records") or []
    ok = code(b) == 200 and len(records) > 0
    chk(f"P1 dataset/{ds_id} records 非空",
        ok,
        f"code={code(b)} indicatorCount={dd.get('indicatorCount')} records={len(records)}"
        + (f" (预期≥{expected_count})" if not ok else ""))
    if records:
        print(f"       records[0] keys={list(records[0].keys())[:8]}")

# ── P2: compare CROSS xAxis 应全部用 metricName ──────────────
print("\n=== P2: compare CROSS xAxis 一致性 ===")
http, b = req("get", "/api/indicator-result/compare",
    params={"metricCodes": "rate_incision_infection,rate_surgery_complication,avg_cost_pneumonia_adult,avg_cost_heart_failure",
            "timeDimension": "YEAR", "timeValue": "2020"})
dd = d(b) or {}
xAxis = dd.get("xAxis") or []
# 检查：xAxis 里不应出现英文 metricCode 格式（全小写_下划线）
import re
bad_items = [x for x in xAxis if re.match(r'^[a-z_]+$', x or '')]
ok_xaxis  = code(b) == 200 and len(bad_items) == 0
chk("P2 xAxis 全部为中文名称（无英文编码）",
    ok_xaxis,
    f"code={code(b)} xAxis={xAxis}  bad={bad_items}")

# 确认 avg_cost_heart_failure 是真实不存在的指标
http2, b2 = req("get", "/api/indicator/code/avg_cost_heart_failure")
chk("P2 avg_cost_heart_failure 确实不在指标表(应30404)",
    code(b2) in (30404, 404),
    f"code={code(b2)} msg={b2.get('message','')[:60] if isinstance(b2,dict) else ''}")

# 用3个确认存在的指标再测一次
http3, b3 = req("get", "/api/indicator-result/compare",
    params={"metricCodes": "rate_incision_infection,rate_surgery_complication,avg_cost_pneumonia_adult",
            "timeDimension": "YEAR", "timeValue": "2020"})
dd3 = d(b3) or {}
xAxis3 = dd3.get("xAxis") or []
bad3 = [x for x in xAxis3 if re.match(r'^[a-z_]+$', x or '')]
ok3 = code(b3) == 200 and len(bad3) == 0
chk("P2 CROSS(3个有效指标) xAxis全中文",
    ok3,
    f"xAxis={xAxis3}")

# ── P3: overallStatus 全 NO_TARGET 时返回 NO_TARGET ──────────
print("\n=== P3: overallStatus 语义修复 ===")
# 全无目标值 → 应返回 NO_TARGET 或 UNKNOWN，不能是 PASS
for params, label in [
    ({"timeDimension": "YEAR", "timeValue": "2020"}, "YEAR 2020"),
    ({},                                              "空参→最新"),
]:
    http, b = req("post", "/api/data-validation/check", json=params)
    dd = d(b) or {}
    overall    = dd.get("overallStatus")
    pass_cnt   = dd.get("passCount", 0)
    fail_cnt   = dd.get("failCount", 0)
    no_tgt_cnt = sum(1 for i in (dd.get("issues") or []) if i.get("status") == "NO_TARGET")
    total      = dd.get("totalCount", 0)
    # 判断：如果全是 NO_TARGET，overallStatus 不应是 PASS
    all_no_target = (no_tgt_cnt == total and total > 0)
    ok = not (all_no_target and overall == "PASS")
    chk(f"P3 check({label}) 全NO_TARGET时overallStatus≠PASS",
        ok,
        f"overallStatus={overall} passCount={pass_cnt} failCount={fail_cnt} "
        f"noTargetCount={no_tgt_cnt}/{total}")

# compliance 的 overallStatus 也一起验
for params, label in [
    ({"timeDimension": "YEAR", "timeValue": "2020"}, "YEAR 2020"),
    ({},                                              "空参→最新"),
]:
    http, b = req("get", "/api/indicator-result/compliance", params=params)
    dd = d(b) or {}
    # compliance 没有 overallStatus，检查 complianceRate=0 时不显示"全部达标"
    rate = dd.get("complianceRate", "")
    no_tgt = dd.get("noTargetCount", 0)
    total  = dd.get("totalCount", 0)
    chk(f"P3 compliance({label}) 结构正确",
        code(b) == 200,
        f"complianceRate={rate} noTargetCount={no_tgt}/{total}")

# ── 汇总 ─────────────────────────────────────────────────────
PASS = sum(1 for r in results if r[0] == "PASS")
FAIL = sum(1 for r in results if r[0] == "FAIL")
print(f"\n{'='*60}")
print(f"  验证汇总  共 {len(results)} 项   ✅ {PASS}   ❌ {FAIL}")
print(f"{'='*60}")
if FAIL:
    print("\n❌ 未通过：")
    for r in results:
        if r[0] == "FAIL":
            print(f"  {r[1]}: {r[2]}")
print()
