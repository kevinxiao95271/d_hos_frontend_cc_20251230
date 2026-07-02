"""
新接口探测：data-validation / compliance / dataset / compare
"""
import sys, json, requests
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
    icon = "✅" if ok else "❌"
    print(f"  [{icon}] {label}")
    if detail:
        print(f"       {detail}")

def req(method, path, **kw):
    try:
        r = getattr(requests, method)(f"{BASE}{path}", headers=H, timeout=20, **kw)
        try: b = r.json()
        except Exception: b = {"_raw": r.text[:300], "_http": r.status_code}
        return r.status_code, b
    except Exception as e:
        return 0, {"error": str(e)}

def code(b): return b.get("code") if isinstance(b, dict) else "?"
def msg(b):  return b.get("message", "")[:80] if isinstance(b, dict) else str(b)[:80]
def data(b): return b.get("data") if isinstance(b, dict) else None

# ══════════════════════════════════════════════════════════════
print("\n══ 一、数据质检 /api/data-validation ══════════════")

# 1. check - 推荐入参
print("\n--- POST /api/data-validation/check ---")
http, b = req("post", "/api/data-validation/check",
    json={"timeDimension": "YEAR", "timeValue": "2020"})
ok = http == 200 and code(b) == 200
chk("check(YEAR 2020)", ok, f"code={code(b)} msg={msg(b)}")
if ok:
    d = data(b)
    if isinstance(d, dict):
        print(f"       totalCount={d.get('totalCount')} passCount={d.get('passCount')} "
              f"failCount={d.get('failCount')} overallStatus={d.get('overallStatus')}")
        issues = d.get("issues") or []
        print(f"       issues count={len(issues)}")
        if issues:
            first = issues[0]
            print(f"       issues[0]: metricCode={first.get('metricCode')} "
                  f"status={first.get('status')} msg={first.get('message','')[:50]}")

# 2. check - 指定 metricCodes
http, b = req("post", "/api/data-validation/check",
    json={"timeDimension": "YEAR", "timeValue": "2020",
          "metricCodes": ["rate_incision_infection", "rate_surgery_complication"]})
ok = http == 200 and code(b) == 200
chk("check(YEAR 2020 + metricCodes)", ok, f"code={code(b)} msg={msg(b)}")
if ok and isinstance(data(b), dict):
    print(f"       totalCount={data(b).get('totalCount')} issues={len(data(b).get('issues') or [])}")

# 3. check - 空参数（取最新）
http, b = req("post", "/api/data-validation/check", json={})
ok = http == 200 and code(b) == 200
chk("check(空参数→最新)", ok, f"code={code(b)} msg={msg(b)}")
if ok and isinstance(data(b), dict):
    print(f"       totalCount={data(b).get('totalCount')} overallStatus={data(b).get('overallStatus')}")

# 4. history
print("\n--- GET /api/data-validation/history ---")
http, b = req("get", "/api/data-validation/history", params={"current": 1, "size": 10})
ok = http == 200 and code(b) == 200
chk("history(page)", ok, f"code={code(b)} msg={msg(b)}")
if ok:
    d = data(b)
    records = (d.get("records") or d) if isinstance(d, dict) else (d or [])
    print(f"       records={len(records) if isinstance(records, list) else '?'} total={d.get('total','?') if isinstance(d,dict) else '?'}")
    if isinstance(records, list) and records:
        print(f"       records[0] keys={list(records[0].keys())[:8]}")

http, b = req("get", "/api/data-validation/history",
    params={"timeDimension": "YEAR", "current": 1, "size": 5})
ok = http == 200 and code(b) == 200
chk("history(timeDimension=YEAR)", ok, f"code={code(b)} msg={msg(b)}")

# ══════════════════════════════════════════════════════════════
print("\n══ 二、达标率 /api/indicator-result/compliance ════")

print("\n--- GET /api/indicator-result/compliance ---")
for params, label in [
    ({"timeDimension": "YEAR", "timeValue": "2020"}, "YEAR 2020"),
    ({"timeDimension": "YEAR", "timeValue": "2023"}, "YEAR 2023"),
    ({},                                              "空参→最新"),
]:
    http, b = req("get", "/api/indicator-result/compliance", params=params)
    ok = http == 200 and code(b) == 200
    chk(f"compliance({label})", ok, f"code={code(b)} msg={msg(b)}")
    if ok and isinstance(data(b), dict):
        d = data(b)
        print(f"       totalCount={d.get('totalCount')} passCount={d.get('passCount')} "
              f"noTargetCount={d.get('noTargetCount')} complianceRate={d.get('complianceRate')}")
        items = d.get("items") or []
        if items:
            it = items[0]
            print(f"       items[0]: {it.get('metricCode')} resultValue={it.get('resultValue')} "
                  f"targetValue={it.get('targetValue')} status={it.get('complianceStatus')}")

# ══════════════════════════════════════════════════════════════
print("\n══ 三、数据集管理 /api/dataset ════════════════════")

print("\n--- GET /api/dataset/page ---")
for params, label in [
    ({"current": 1, "size": 10},            "全量分页"),
    ({"type": "YEAR",  "current": 1, "size": 10}, "type=YEAR"),
    ({"type": "MONTH", "current": 1, "size": 10}, "type=MONTH"),
]:
    http, b = req("get", "/api/dataset/page", params=params)
    ok = http == 200 and code(b) == 200
    chk(f"dataset/page({label})", ok, f"code={code(b)} msg={msg(b)}")
    if ok and isinstance(data(b), dict):
        d = data(b)
        recs = d.get("records") or []
        print(f"       total={d.get('total')} records={len(recs)}")
        if recs:
            print(f"       records[0] keys={list(recs[0].keys())}")

print("\n--- GET /api/dataset/list ---")
for params, label in [
    ({},              "全量"),
    ({"type": "YEAR"}, "type=YEAR"),
]:
    http, b = req("get", "/api/dataset/list", params=params)
    ok = http == 200 and code(b) == 200
    chk(f"dataset/list({label})", ok, f"code={code(b)} msg={msg(b)}")
    if ok:
        d = data(b)
        lst = d if isinstance(d, list) else (d.get("records") or [] if isinstance(d, dict) else [])
        print(f"       count={len(lst)}")
        if lst:
            print(f"       [0] keys={list(lst[0].keys())}")

print("\n--- GET /api/dataset/{id} ---")
for ds_id, label in [
    ("YEAR_2020", "YEAR_2020"),
    ("YEAR_2023", "YEAR_2023"),
    ("YEAR_2022", "YEAR_2022"),
    ("YEAR_9999", "不存在的id"),
]:
    http, b = req("get", f"/api/dataset/{ds_id}")
    ok_exists = http == 200 and code(b) == 200
    ok_notfound = ds_id == "YEAR_9999" and code(b) in (30404, 404)
    ok = ok_exists or ok_notfound
    chk(f"dataset/{ds_id}", ok, f"code={code(b)} msg={msg(b)}")
    if ok_exists and isinstance(data(b), dict):
        d = data(b)
        items = d.get("items") or d.get("results") or (d if isinstance(d, list) else [])
        if isinstance(d, dict):
            print(f"       keys={list(d.keys())}")
            results_list = d.get("items") or d.get("indicatorResults") or []
            print(f"       indicator count={len(results_list)}")

# ══════════════════════════════════════════════════════════════
print("\n══ 四、对比分析 /api/indicator-result/compare ═════")

print("\n--- 模式一：趋势分析（单指标 × 多年）---")
http, b = req("get", "/api/indicator-result/compare",
    params={"metricCode": "rate_incision_infection",
            "timeDimension": "YEAR",
            "timeValues": "2020,2021,2023"})
ok = http == 200 and code(b) == 200
chk("compare TREND(rate_incision_infection, 2020,2021,2023)", ok, f"code={code(b)} msg={msg(b)}")
if ok and isinstance(data(b), dict):
    d = data(b)
    print(f"       mode={d.get('mode')} xAxis={d.get('xAxis')} "
          f"series count={len(d.get('series') or [])}")
    for s in (d.get("series") or []):
        print(f"       series: {s.get('metricCode')} data={s.get('data')}")

# 多个有数据的指标
http, b = req("get", "/api/indicator-result/compare",
    params={"metricCode": "rate_surgery_complication",
            "timeDimension": "YEAR",
            "timeValues": "2020,2021,2022,2023"})
ok = http == 200 and code(b) == 200
chk("compare TREND(rate_surgery_complication, 4 years)", ok, f"code={code(b)} msg={msg(b)}")
if ok and isinstance(data(b), dict):
    d = data(b)
    print(f"       xAxis={d.get('xAxis')} series={[(s.get('metricCode'), [x.get('resultValue') for x in (s.get('data') or [])]) for s in (d.get('series') or [])]}")

print("\n--- 模式二：横向对比（多指标 × 单时间段）---")
http, b = req("get", "/api/indicator-result/compare",
    params={"metricCodes": "rate_incision_infection,rate_surgery_complication,avg_cost_pneumonia_adult,avg_cost_heart_failure",
            "timeDimension": "YEAR",
            "timeValue": "2020"})
ok = http == 200 and code(b) == 200
chk("compare CROSS(4 metrics, YEAR 2020)", ok, f"code={code(b)} msg={msg(b)}")
if ok and isinstance(data(b), dict):
    d = data(b)
    print(f"       mode={d.get('mode')} xAxis={d.get('xAxis')}")
    for s in (d.get("series") or []):
        vals = [x.get("resultValue") for x in (s.get("data") or [])]
        print(f"       {s.get('metricCode')}: {vals}")

# 边界：只传 timeValues 不传 metricCode（缺参应报错）
print("\n--- 边界/异常测试 ---")
http, b = req("get", "/api/indicator-result/compare",
    params={"timeDimension": "YEAR", "timeValues": "2020,2021"})
ok = code(b) != 200
chk("compare(缺 metricCode/metricCodes 应报错)", ok, f"code={code(b)} msg={msg(b)}")

# timeValues 超多（如10年）
http, b = req("get", "/api/indicator-result/compare",
    params={"metricCode": "rate_incision_infection",
            "timeDimension": "YEAR",
            "timeValues": "2015,2016,2017,2018,2019,2020,2021,2022,2023,2024"})
ok = http == 200  # 只要不崩即可
chk("compare TREND(10年，看是否有限制)", ok, f"code={code(b)} msg={msg(b)[:60]}")

# ══════════════════════════════════════════════════════════════
PASS = sum(1 for r in results if r[0] == "PASS")
FAIL = sum(1 for r in results if r[0] == "FAIL")
print(f"\n{'='*60}")
print(f"  探测汇总  共 {len(results)} 项   ✅ {PASS}   ❌ {FAIL}")
print(f"{'='*60}")
if FAIL:
    print("\n❌ 失败明细：")
    for r in results:
        if r[0] == "FAIL":
            print(f"  {r[1]}: {r[2]}")
print()
